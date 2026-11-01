import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    root: Path
    port: int = 8420
    span: int = 20
    host: str = "127.0.0.1"
    owner_access_listener: tuple[str, int] | None = None
    supervisor_listener: tuple[str, int, Path, Path] | None = None

    @property
    def home(self) -> Path:
        return self.root / ".journal"

    @property
    def database(self) -> Path:
        return self.home / "journal.db"

    @property
    def status_home(self) -> Path:
        return Path.home() / ".journal" / "status"

    @property
    def files(self) -> Path:
        return self.home / "files"

    @property
    def readers(self) -> Path:
        return self.home / "readers"

    @property
    def port_file(self) -> Path:
        return self.home / "port"

    def ports(self) -> tuple[int, ...]:
        if self.port == 0:
            return (0,)
        return tuple(dict.fromkeys((*self.stored_port(), *range(self.port, self.port + self.span))))

    def stored_port(self) -> tuple[int, ...]:
        if not self.port_file.is_file():
            return ()
        text = self.port_file.read_text().strip()
        return (int(text),) if text.isdigit() else ()

    @classmethod
    def rooted(cls, root: Path) -> "Config":
        port = int(os.environ.get("JOURNAL_PORT", "8420"))
        span = 1 if "JOURNAL_PORT" in os.environ else 20
        owner_values = tuple(
            os.environ.get(name, "")
            for name in ("JOURNAL_OWNER_ACCESS_HOST", "JOURNAL_OWNER_ACCESS_PORT")
        )
        if any(owner_values) and not all(owner_values):
            raise ValueError("the owner access listener requires a host and port")
        owner_access_listener = (owner_values[0], int(owner_values[1])) if all(owner_values) else None
        supervisor_values = tuple(
            os.environ.get(name, "")
            for name in (
                "JOURNAL_SUPERVISOR_HOST",
                "JOURNAL_SUPERVISOR_PORT",
                "JOURNAL_SUPERVISOR_TLS_CERT_FILE",
                "JOURNAL_SUPERVISOR_TLS_KEY_FILE",
            )
        )
        if any(supervisor_values) and not all(supervisor_values):
            raise ValueError("the supervisor listener requires a host, port, TLS certificate and TLS key")
        supervisor_listener = (
            supervisor_values[0],
            int(supervisor_values[1]),
            Path(supervisor_values[2]),
            Path(supervisor_values[3]),
        ) if all(supervisor_values) else None
        return cls(
            root.resolve(),
            port,
            span,
            os.environ.get("JOURNAL_HOST", "127.0.0.1"),
            owner_access_listener,
            supervisor_listener,
        )
