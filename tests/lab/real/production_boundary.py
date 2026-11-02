import hashlib
import json
import os
import platform
import secrets
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Mapping

from tests.lab.real.isolation_evidence import IsolationEvidence


TMUX_SOCKET_PATH_LIMIT = 104


def developer_tool_paths() -> tuple[Path, ...]:
    """The selected developer directory, so /usr/bin/git inside the sandbox finds its tools instead of asking macOS to install them."""
    selected = subprocess.run(["/usr/bin/xcode-select", "-p"], capture_output=True, text=True, check=False).stdout.strip()
    if not selected:
        return ()
    developer = Path(selected).resolve()
    bundle = next((parent for parent in (developer, *developer.parents) if parent.suffix == ".app"), developer)
    return (bundle,)


class ProductionBoundary:
    """Confine run processes to private storage and provider-only HTTPS egress."""

    def __init__(self, run_id: str, ports: tuple[int, ...], read_paths: tuple[Path, ...] = ()) -> None:
        self.run_id, self.ports = run_id, ports
        self.read_paths = read_paths
        self.profile: Path | None = None
        self.root: Path | None = None
        self.sandbox = Path(shutil.which("sandbox-exec") or "")
        self.tmux_mount = Path("/private/tmp") / f"jl-{secrets.token_hex(6)}"
        self.tmux_tmpdir = self.tmux_mount

    @property
    def tmux_socket_path(self) -> Path:
        return self.tmux_tmpdir / f"tmux-{os.getuid()}" / "default"

    def verify(self, run_id: str, paths: Mapping[str, Path]) -> IsolationEvidence:
        if platform.system() != "Darwin" or not self.sandbox.is_file():
            raise ValueError("macOS sandbox-exec is required for subscription run isolation")
        if run_id != self.run_id or len(set(self.ports)) != len(self.ports):
            raise ValueError("run isolation ports must be unique and bound to this run")
        if any(type(port) is not int or not 1 <= port <= 65535 for port in self.ports):
            raise ValueError("run isolation ports must be valid loopback ports")
        self.root = paths["root"].resolve()
        if paths["tmp"] != self.tmux_tmpdir:
            raise ValueError("run temporary directory and tmux socket directory must be the same short private path")
        self.verify_tmux_directory(paths)
        self.profile = paths["runtime"] / "run-boundary.sb"
        private_reads = tuple(path for key, path in paths.items() if key.startswith("provider_config_"))
        try:
            self.profile.write_text(self.policy(self.root, (*self.read_paths, *private_reads)), encoding="utf-8")
            self.profile.chmod(0o600)
        except OSError:
            self.close()
            raise
        return self.evidence(paths)

    def observe(self, run_id: str) -> IsolationEvidence:
        if run_id != self.run_id or self.profile is None or not self.profile.is_file():
            raise ValueError("run isolation profile disappeared before observation")
        return self.evidence({"root": self.root})

    def wrap(self, command: list[str]) -> list[str]:
        if self.profile is None:
            raise ValueError("run isolation must be verified before starting a process")
        return [str(self.sandbox), "-f", str(self.profile), *command]

    def evidence(self, paths: Mapping[str, Path]) -> IsolationEvidence:
        root = Path(paths["root"]).resolve()
        profile_digest = hashlib.sha256(self.profile.read_bytes()).hexdigest() if self.profile else "unverified"
        writable = tuple(sorted(str(Path(paths[key]).resolve()) for key in ("project", "private_home", "runtime", "tmp"))) if "project" in paths else tuple(
            tuple(sorted([*(str(root / name) for name in ("project", "home", "runtime")),
                          str(self.tmux_tmpdir)]))
        )
        return IsolationEvidence(self.run_id, str(root), writable, f"seatbelt:{self.run_id}", profile_digest,
                                 True, True, True, True)

    def verify_tmux_directory(self, paths: Mapping[str, Path]) -> None:
        if paths["tmp"] != self.tmux_tmpdir or not self.tmux_directory_is_valid():
            raise ValueError("tmux socket storage must be this run's private short temp directory")

    def tmux_directory_is_valid(self) -> bool:
        return (self.tmux_tmpdir.parent == Path("/private/tmp") and not self.tmux_tmpdir.is_symlink()
                and self.tmux_tmpdir.is_dir() and stat.S_IMODE(self.tmux_tmpdir.stat().st_mode) & 0o077 == 0)

    def close(self) -> bool:
        if not self.tmux_mount.exists():
            return True
        if not self.tmux_tmpdir.is_dir() or self.tmux_tmpdir.is_symlink():
            return False
        shutil.rmtree(self.tmux_tmpdir)
        return True

    def policy(self, root: Path, read_paths: tuple[Path, ...]) -> str:
        allowed_ports = "\n".join(f'(allow network-outbound (remote ip "localhost:{port}"))' for port in self.ports)
        bound_ports = "\n".join(
            f'(allow network-bind (local ip "localhost:{port}"))\n(allow network-inbound (local ip "localhost:{port}"))'
            for port in self.ports
        )
        shell_resolution = Path("/private/var/select/sh")
        metadata_paths = tuple(dict.fromkeys(
            parent for path in (root, *read_paths, shell_resolution, self.tmux_mount, self.tmux_tmpdir)
            for parent in (path, *path.parents, path.resolve(), *path.resolve().parents) if parent != Path("/")
        ))
        return "\n".join((
            "(version 1)",
            "(deny default)",
            "(allow process*)",
            "(allow file-map-executable)",
            "(allow sysctl-read)",
            "(allow mach-lookup)",
            *(f'(allow file-read* (subpath {json.dumps(str(path))}))' for path in (
                Path("/System"), Path("/Library"), Path("/usr"), Path("/bin"), Path("/sbin"),
                Path("/private/etc"), Path("/opt/homebrew"), Path("/dev"), *developer_tool_paths(),
            )),
            *(f'(allow file-read-metadata (literal {json.dumps(str(path))}))' for path in metadata_paths),
            *(f'(allow file-read* (literal {json.dumps(str(path.resolve()))}))' for path in read_paths),
            *(f'(allow file-read* (subpath {json.dumps(str(path.resolve()))}))' for path in read_paths),
            f'(allow file-read* (literal {json.dumps(str(shell_resolution))}))',
            f'(allow file-read* (literal {json.dumps(str(self.tmux_tmpdir))}))',
            '(allow file-read* (literal "/"))',
            f'(allow file-read* (subpath {json.dumps(str(root))}))',
            f"(allow file-write* (subpath {json.dumps(str(root))}))",
            f'(allow file-read* (subpath {json.dumps(str(self.tmux_tmpdir))}))',
            f'(allow file-write* (subpath {json.dumps(str(self.tmux_tmpdir))}))',
            '(allow file-write* (literal "/dev/null"))',
            allowed_ports,
            bound_ports,
            "",
        ))
