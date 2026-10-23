import json
from sqlite3 import Row

from sync_server.db.store import Store


class HostRequestRows:
    """The SQL of the host_requests table: a write asked of an environment's host, by the environment's key, waiting until the host has made it, and then naming who made it."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def insert(self, environment_key: str, kind: str, body: dict, account_id: int, created_at: float) -> int:
        return self.store.execute("INSERT INTO host_requests (environment_key, kind, body, account_id, created_at) VALUES (?, ?, ?, ?, ?)", (environment_key, kind, json.dumps(body), account_id, created_at)).lastrowid

    def waiting(self, environment_keys: tuple[str, ...]) -> list[Row]:
        placeholders = ", ".join("?" for _ in environment_keys)
        return self.store.all(f"SELECT id, environment_key, kind, body, account_id, created_at FROM host_requests WHERE finished_at = 0 AND environment_key IN ({placeholders}) ORDER BY id", environment_keys) if environment_keys else []

    def finish(self, id: int, host_id: int, finished_at: float) -> None:
        self.store.execute("UPDATE host_requests SET host_id = ?, finished_at = ? WHERE id = ?", (host_id, finished_at, id))

    def is_vouched(self, host_id: int, account_id: int) -> bool:
        return self.store.one("SELECT 1 FROM host_requests WHERE host_id = ? AND account_id = ? LIMIT 1", (host_id, account_id)) is not None
