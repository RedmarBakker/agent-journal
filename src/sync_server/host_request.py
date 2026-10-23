import json
from dataclasses import dataclass
from sqlite3 import Row


@dataclass(frozen=True)
class HostRequest:
    """A write asked of an environment's host: its number, the environment's key, what kind of write it is with what it carries, the account that asked and when."""

    id: int
    environment_key: str
    kind: str
    body: dict
    account_id: int
    created_at: float

    @classmethod
    def stored(cls, row: Row) -> "HostRequest":
        return cls(row["id"], row["environment_key"], row["kind"], json.loads(row["body"]), row["account_id"], row["created_at"])
