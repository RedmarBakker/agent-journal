from dataclasses import dataclass
from urllib.parse import urlsplit

from journal.support.rejection import Rejection


@dataclass(frozen=True)
class SentryAddress:
    """A Sentry project's DSN read into where an event is posted and the public key that signs it."""

    envelope_url: str
    public_key: str
    dsn: str

    @classmethod
    def parsed(cls, dsn: str) -> "SentryAddress":
        parts = urlsplit(dsn.strip())
        project = parts.path.strip("/").split("/")[-1]
        if not parts.username or not parts.hostname or not project.isdigit():
            raise Rejection(f"{dsn!r} is no Sentry DSN: it reads https://<key>@<host>/<project number>")
        port = f":{parts.port}" if parts.port else ""
        return cls(f"{parts.scheme}://{parts.hostname}{port}/api/{project}/envelope/", parts.username, dsn.strip())
