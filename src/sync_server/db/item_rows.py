from sqlite3 import Row

from sync_server.db.store import Store


class ItemRows:
    """The SQL of the items table: one row per published item, by its type and name."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def insert(self, item_type: str, name: str, description: str, publisher_id: int, created_at: float) -> int:
        return self.store.execute("INSERT INTO items (item_type, name, description, publisher_id, created_at) VALUES (?, ?, ?, ?, ?)", (item_type, name, description, publisher_id, created_at)).lastrowid

    def numbered(self, id: int) -> Row | None:
        return self.store.one("SELECT id, item_type, name, description, publisher_id, created_at, withdrawn_at FROM items WHERE id = ?", (id,))

    def item_row(self, item_type: str, name: str) -> Row | None:
        return self.store.one("SELECT id, item_type, name, description, publisher_id, created_at, withdrawn_at FROM items WHERE item_type = ? AND name = ?", (item_type, name))

    def listed(self) -> list[Row]:
        return self.store.all("SELECT id, item_type, name, description, publisher_id, created_at, withdrawn_at FROM items WHERE withdrawn_at = 0 ORDER BY item_type, name")

    def withdraw(self, id: int, withdrawn_at: float) -> None:
        self.store.execute("UPDATE items SET withdrawn_at = ? WHERE id = ?", (withdrawn_at, id))
