from dataclasses import dataclass
from sqlite3 import Row

from sync_server.account import Account


@dataclass(frozen=True)
class Item:
    """A published item of the library: its type and name, what it is for, who first published it, and when it was withdrawn, 0 while it is listed; its owners are that publisher and every admin."""

    id: int
    item_type: str
    name: str
    description: str
    publisher_id: int
    withdrawn_at: float

    @classmethod
    def read(cls, row: Row | dict) -> "Item":
        return cls(row["id"], row["item_type"], row["name"], row["description"], row["publisher_id"], row["withdrawn_at"])

    def has_owner(self, account: Account) -> bool:
        return account.id == self.publisher_id or account.is_admin()
