import fcntl
import json
import os
import re
import shlex
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Mapping

from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL
from journal.providers.support.helper_setup import JOURNAL_ACTIVE
from tests.lab.real.isolation_evidence import IsolationEvidence


RUN_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
BLOCKED_PREFIXES = ("JOURNAL_", "CLAUDE_", "CODEX_", "AGENT_", "DYLD_")
BLOCKED_NAMES = frozenset({ACTOR, ACTOR_TOKEN, AGENT_SHELL, JOURNAL_ACTIVE, "JOURNAL_LAUNCH", "JOURNAL_SESSION",
                           "JOURNAL_PORT", "JOURNAL_ROOT", "BASH_ENV", "ENV", "PROMPT_COMMAND", "PYTHONPATH",
                           "PYTHONHOME", "LD_PRELOAD"})
class IsolatedJournal:
    """Create a fresh private run root and refuse launch until an OS boundary proves its scope."""

    def __init__(self, lab_home: Path, checkout: Path, protected_paths: tuple[Path, ...] = ()) -> None:
        self.lab_home, self.checkout = lab_home, checkout
        self.protected_paths = (checkout, *protected_paths)

    def run_root(self, batch_id: str, run_id: str) -> Path:
        self.name(batch_id)
        self.name(run_id)
        self.validate_home()
        return self.lab_home.resolve() / "roots" / batch_id / run_id

    def prepare(self, batch_id: str, run_id: str, boundary: object | None) -> dict[str, Path]:
        root = self.run_root(batch_id, run_id)
        self.validate_root(root)
        with self.lock():
            if root.exists():
                raise ValueError("an isolated run root is never reused")
            roots = root.parent.parent
            self.private_directory(roots)
            self.private_directory(root.parent)
            root.mkdir(mode=0o700)
            paths = self.paths(root)
            for name in ("project", "private_home", "runtime", "evidence", "tmp", "xdg_config", "xdg_cache", "bin"):
                paths[name].mkdir(mode=0o700)
            try:
                if boundary is None or not hasattr(boundary, "verify"):
                    raise ValueError("OS-enforced isolation boundary is unavailable; real run refused")
                evidence = boundary.verify(run_id, paths)
                self.validate_start_boundary(evidence, paths, run_id)
                self.write_evidence(paths, "isolation-start.json", evidence)
            except Exception as error:
                self.setup_failed(paths, run_id, str(error))
                raise
            return paths

    def child_environment(self, paths: Mapping[str, Path], host: Mapping[str, str], allowed: tuple[str, ...],
                          provider_markers: tuple[str, ...], credential_names: tuple[str, ...], port: int,
                          actor: str, token: str, path_entries: tuple[Path, ...]) -> dict[str, str]:
        if type(port) is not int or not 1 <= port <= 65535 or not actor or not token:
            raise ValueError("isolated journal endpoints need a valid port and fresh actor credentials")
        shim = paths["bin"] / "journal"
        if not shim.is_file() or shim.is_symlink() or not os.access(shim, os.X_OK):
            raise ValueError("the isolated journal shim must be installed before building the child environment")
        blocked = set(provider_markers) | BLOCKED_NAMES
        env = {key: host[key] for key in (*allowed, *credential_names) if key in host and key not in blocked
               and not key.startswith(BLOCKED_PREFIXES)}
        if any(not entry.is_absolute() for entry in path_entries):
            raise ValueError("isolated PATH cannot include a global journal dispatcher")
        path = (paths["bin"].resolve(), *(entry.resolve() for entry in path_entries))
        if any((entry / "journal").exists() for entry in path[1:]):
            raise ValueError("isolated PATH cannot resolve a global journal dispatcher")
        env.update({
            "HOME": str(paths["private_home"].resolve()),
            "XDG_CONFIG_HOME": str(paths["xdg_config"].resolve()),
            "XDG_CACHE_HOME": str(paths["xdg_cache"].resolve()),
            "TMPDIR": str(paths["tmp"].resolve()),
            "TMP": str(paths["tmp"].resolve()),
            "TEMP": str(paths["tmp"].resolve()),
            "PATH": os.pathsep.join(map(str, path)),
            "JOURNAL_ROOT": str(paths["project"].resolve()),
            "JOURNAL_PORT": str(port),
            AGENT_SHELL: "1",
            ACTOR: actor,
            ACTOR_TOKEN: token,
            JOURNAL_ACTIVE: "1",
        })
        return env

    @staticmethod
    def install_journal_shim(paths: Mapping[str, Path], port: int) -> Path:
        if type(port) is not int or not 1 <= port <= 65535:
            raise ValueError("isolated journal shim needs a valid private port")
        project_path = paths["project"]
        project = project_path.resolve()
        target = project_path / "src" / "journal.sh"
        target_chain = (target, *target.parents)
        if (not target.is_absolute() or not target.is_file() or
                any(part.is_symlink() for part in target_chain if part == project_path or part.is_relative_to(project_path)) or
                not target.resolve().is_relative_to(project)):
            raise ValueError("isolated project snapshot must contain its own journal command")
        directory = paths["bin"]
        if directory.is_symlink() or not directory.is_dir() or stat.S_IMODE(directory.stat().st_mode) & 0o077:
            raise ValueError("isolated journal command directory must be private")
        shim = directory / "journal"
        content = ("#!/bin/sh\n"
                   f"export JOURNAL_ROOT={shlex.quote(str(project))}\n"
                   f"export JOURNAL_PORT={port}\n"
                   f"exec /bin/sh {shlex.quote(str(target.resolve()))} \"$@\"\n")
        descriptor = os.open(shim, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o700)
        with os.fdopen(descriptor, "w", encoding="utf-8") as target_file:
            target_file.write(content)
            target_file.flush()
            os.fsync(target_file.fileno())
        return shim

    def observe_boundary(self, boundary: object, run_id: str, paths: Mapping[str, Path]) -> IsolationEvidence:
        if not hasattr(boundary, "observe"):
            raise ValueError("OS isolation observer is unavailable after the real run")
        evidence = boundary.observe(run_id)
        self.validate_boundary(evidence, paths, run_id)
        self.write_evidence(paths, "isolation-observation.json", evidence)
        return evidence

    @classmethod
    def validate_boundary(cls, evidence: object, paths: Mapping[str, Path], run_id: str) -> None:
        if not isinstance(evidence, IsolationEvidence):
            raise ValueError("OS boundary must return structured isolation evidence")
        expected_writable = tuple(sorted(str(paths[key].resolve()) for key in ("project", "private_home", "runtime", "tmp")))
        if evidence.run_id != run_id or evidence.root != str(paths["root"].resolve()) or evidence.writable_paths != expected_writable:
            raise ValueError("OS boundary evidence does not match the isolated run roots")
        if not all((evidence.filesystem_boundary, evidence.process_boundary, evidence.write_observer_active, evidence.stop_on_escape)):
            raise ValueError("OS boundary must enforce filesystem and process scope, observe writes and stop on escape")
    @classmethod
    def validate_start_boundary(cls, evidence: object, paths: Mapping[str, Path], run_id: str) -> None:
        cls.validate_boundary(evidence, paths, run_id)
        if evidence.escaped_writes:
            raise ValueError("OS boundary recorded an escaped write before the run started")

    @staticmethod
    def write_evidence(paths: Mapping[str, Path], name: str, evidence: IsolationEvidence) -> None:
        path = paths["evidence"] / name
        if path.is_symlink():
            raise ValueError("isolation evidence cannot replace a symlink")
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as target:
            json.dump(evidence.to_document(), target, sort_keys=True, separators=(",", ":"), allow_nan=False)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())

    @staticmethod
    def verify_identity(identity: Mapping[str, object], root: Path, run_id: str, launch_id: str,
                        challenge: str, port: int) -> None:
        expected = {"root": str((root / "project" / ".journal").resolve()), "run_id": run_id, "launch_id": launch_id,
                    "challenge": challenge, "host": "127.0.0.1", "port": port, "authenticated": True}
        if any(identity.get(key) != value for key, value in expected.items()) or type(identity.get("pid")) is not int or identity["pid"] <= 0:
            raise ValueError("journal endpoint identity does not match the isolated run")

    @staticmethod
    def setup_failed(paths: Mapping[str, Path], run_id: str, reason: str) -> None:
        record = {"run_id": run_id, "terminal_reason": "setup_failed", "reason": reason}
        path = paths["evidence"] / "setup-failed.json"
        path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
        path.chmod(0o600)

    def validate_home(self) -> None:
        if not self.lab_home.is_absolute() or not self.checkout.is_absolute():
            raise ValueError("LAB_HOME and the controlling checkout must be absolute paths")
        if self.has_symlink(self.lab_home) or self.lab_home.exists() and not self.lab_home.is_dir():
            raise ValueError("LAB_HOME must be a real directory without symlink aliases")
        if self.lab_home.exists() and stat.S_IMODE(self.lab_home.stat().st_mode) & 0o077:
            raise ValueError("LAB_HOME must be private to its owner")
        resolved = self.lab_home.resolve(strict=False)
        self.outside_protected(resolved)

    def validate_root(self, root: Path) -> None:
        if self.has_symlink(root.parent) or root.exists() and self.has_symlink(root):
            raise ValueError("isolated run paths cannot contain symlink aliases")
        self.outside_protected(root.resolve(strict=False))

    def outside_protected(self, candidate: Path) -> None:
        for protected in self.protected_paths:
            if not protected.is_absolute():
                raise ValueError("protected paths must be absolute")
            target = protected.resolve(strict=False)
            if self.overlaps(candidate, target):
                raise ValueError(f"isolated writable path overlaps protected path {target}")

    @staticmethod
    def overlaps(first: Path, second: Path) -> bool:
        return first == second or first.is_relative_to(second) or second.is_relative_to(first)

    @staticmethod
    def paths(root: Path) -> dict[str, Path]:
        return {"root": root, "project": root / "project", "private_home": root / "home", "runtime": root / "runtime",
                "evidence": root / "evidence", "tmp": root / "tmp", "xdg_config": root / "home" / "config",
                "xdg_cache": root / "home" / "cache", "bin": root / "home" / "bin"}

    @staticmethod
    def name(value: str) -> None:
        if not RUN_NAME.fullmatch(value):
            raise ValueError("batch and run ids must be simple names")

    @staticmethod
    def has_symlink(path: Path) -> bool:
        return any(part.is_symlink() for part in (path, *path.parents))

    @contextmanager
    def lock(self):
        if not self.lab_home.parent.is_dir():
            raise ValueError("LAB_HOME parent must already exist")
        self.private_directory(self.lab_home)
        if stat.S_IMODE(self.lab_home.stat().st_mode) & 0o077:
            raise ValueError("LAB_HOME must be private to its owner")
        path = self.lab_home / ".run-roots.lock"
        if path.is_symlink():
            raise ValueError("run-root lock cannot be a symlink")
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
                raise ValueError("run-root lock must be a private regular file")
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    @staticmethod
    def private_directory(path: Path) -> None:
        if path.is_symlink():
            raise ValueError("isolated run directories cannot be symlinks")
        if not path.exists():
            path.mkdir(mode=0o700)
        if not path.is_dir() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise ValueError("isolated run directories must be private to their owner")
