from sqlite3 import Row

from sync_server.db.store import Store

COLUMNS = "id, item_id, number, body, body_hash, lowest_version, note, publisher_id, published_at, completed_at"


class ItemVersionRows:
    """The SQL of the item_versions table: each numbered version of an item, its body and its hash, complete once its files are all in."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def insert(self, item_id: int, number: int, body: str, body_hash: str, lowest_version: str, note: str, publisher_id: int, published_at: float) -> int:
        return self.store.execute("INSERT INTO item_versions (item_id, number, body, body_hash, lowest_version, note, publisher_id, published_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (item_id, number, body, body_hash, lowest_version, note, publisher_id, published_at)).lastrowid

    def numbered(self, item_id: int, number: int) -> Row | None:
        return self.store.one(f"SELECT {COLUMNS} FROM item_versions WHERE item_id = ? AND number = ?", (item_id, number))

    def highest_number(self, item_id: int) -> int:
        return self.store.one("SELECT COALESCE(MAX(number), 0) AS highest FROM item_versions WHERE item_id = ?", (item_id,))["highest"]

    def complete(self, item_id: int) -> list[Row]:
        return self.store.all(f"SELECT {COLUMNS} FROM item_versions WHERE item_id = ? AND completed_at > 0 ORDER BY number", (item_id,))

    def mark_complete(self, id: int, completed_at: float) -> None:
        self.store.execute("UPDATE item_versions SET completed_at = ? WHERE id = ?", (completed_at, id))

    def incomplete(self, item_id: int) -> list[Row]:
        return self.store.all(f"SELECT {COLUMNS} FROM item_versions WHERE item_id = ? AND completed_at = 0 ORDER BY number", (item_id,))

    def delete(self, id: int) -> None:
        self.store.execute("DELETE FROM item_versions WHERE id = ?", (id,))
