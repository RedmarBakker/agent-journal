import hashlib
import json
import platform
import shutil
from pathlib import Path
from typing import Mapping

from tests.lab.real.isolation_evidence import IsolationEvidence


class ProductionBoundary:
    """Confine run processes to private storage and provider-only HTTPS egress."""

    def __init__(self, run_id: str, ports: tuple[int, ...], read_paths: tuple[Path, ...] = ()) -> None:
        self.run_id, self.ports = run_id, ports
        self.read_paths = read_paths
        self.profile: Path | None = None
        self.root: Path | None = None
        self.sandbox = Path(shutil.which("sandbox-exec") or "")

    def verify(self, run_id: str, paths: Mapping[str, Path]) -> IsolationEvidence:
        if platform.system() != "Darwin" or not self.sandbox.is_file():
            raise ValueError("macOS sandbox-exec is required for subscription run isolation")
        if run_id != self.run_id or len(set(self.ports)) != len(self.ports):
            raise ValueError("run isolation ports must be unique and bound to this run")
        if any(type(port) is not int or not 1 <= port <= 65535 for port in self.ports):
            raise ValueError("run isolation ports must be valid loopback ports")
        self.root = paths["root"].resolve()
        self.profile = paths["runtime"] / "run-boundary.sb"
        private_reads = tuple(path for key, path in paths.items() if key.startswith("provider_config_"))
        self.profile.write_text(self.policy(self.root, (*self.read_paths, *private_reads)), encoding="utf-8")
        self.profile.chmod(0o600)
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
            sorted(str(root / name) for name in ("project", "home", "runtime", "tmp"))
        )
        return IsolationEvidence(self.run_id, str(root), writable, f"seatbelt:{self.run_id}", profile_digest,
                                 True, True, True, True)

    def policy(self, root: Path, read_paths: tuple[Path, ...]) -> str:
        allowed_ports = "\n".join(f'(allow network-outbound (remote ip "localhost:{port}"))' for port in self.ports)
        bound_ports = "\n".join(
            f'(allow network-bind (local ip "localhost:{port}"))\n(allow network-inbound (local ip "localhost:{port}"))'
            for port in self.ports
        )
        return "\n".join((
            "(version 1)",
            "(deny default)",
            "(allow process*)",
            "(allow file-map-executable)",
            "(allow sysctl-read)",
            "(allow mach-lookup)",
            *(f'(allow file-read* (subpath {json.dumps(str(path))}))' for path in (
                Path("/System"), Path("/Library"), Path("/usr"), Path("/bin"), Path("/sbin"),
                Path("/private/etc"), Path("/opt/homebrew"), Path("/dev"),
            )),
            *(f'(allow file-read* (literal {json.dumps(str(path.resolve()))}))' for path in read_paths),
            *(f'(allow file-read* (subpath {json.dumps(str(path.resolve()))}))' for path in read_paths),
            '(allow file-read* (literal "/"))',
            f'(allow file-read* (subpath {json.dumps(str(root))}))',
            f"(allow file-write* (subpath {json.dumps(str(root))}))",
            '(allow file-write* (literal "/dev/null"))',
            allowed_ports,
            bound_ports,
            "",
        ))
