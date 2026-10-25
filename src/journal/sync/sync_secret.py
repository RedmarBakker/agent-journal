import hmac
import os
import secrets
from collections.abc import Mapping

from journal.config import Config

SECRET_FILE = "sync-secret"
SECRET_HEADER = "x-journal-sync-secret"
# the version of the sync desk's doors, which the sync service names on every call and the server answers only when it is its own
DESK_PROTOCOL = 3
PROTOCOL_HEADER = "x-journal-desk-protocol"


class SyncSecret:
    """The secret the journal server writes at boot for the services beside it alone, readable by its owner only: a service's registration and a request to the sync desk's doors carry it, and one passed on by a proxy is refused, so no other local process and nothing from outside writes rows as the team."""

    def __init__(self, config: Config) -> None:
        self.path = config.home / "runtime" / SECRET_FILE
        self.value = ""

    def issued(self) -> None:
        self.value = secrets.token_hex(32)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w") as file:
            file.write(self.value)

    def allows(self, headers: Mapping[str, str]) -> bool:
        return bool(self.value) and "x-forwarded-for" not in headers and hmac.compare_digest(headers.get(SECRET_HEADER, ""), self.value)
