import json
from dataclasses import dataclass
from sqlite3 import Row

from sync_server.request_audience import RequestAudience


@dataclass(frozen=True)
class HostRequest:
    """A write asked of another machine: its number, the environment's key, what kind of write it is with what it carries, the account that asked and when, who takes it up (the environment's host, the pool or one device), the device it is addressed to, and the journal version a pool machine must run to take it."""

    id: int
    environment_key: str
    kind: str
    body: dict
    account_id: int
    created_at: float
    audience: str = RequestAudience.HOST
    device_id: int = 0
    version: str = ""

    @classmethod
    def stored(cls, row: Row) -> "HostRequest":
        return cls(row["id"], row["environment_key"], row["kind"], json.loads(row["body"]), row["account_id"], row["created_at"], row["audience"], row["device_id"], row["version"])
