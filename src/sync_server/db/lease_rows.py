from sqlite3 import Row

from sync_server.db.store import Store


class LeaseRows:
    """The SQL of the leases table: one row per name, the device and account holding it, when it was last renewed and how long it stands unrenewed, read with the device's name."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def current(self, name: str) -> Row | None:
        return self.store.one("SELECT leases.name, leases.device_id, leases.account_id, leases.renewed_at, leases.lapse_seconds, coalesce(devices.name, '') AS device_name FROM leases LEFT JOIN devices ON devices.id = leases.device_id WHERE leases.name = ?", (name,))

    def write(self, name: str, device_id: int, account_id: int, renewed_at: float, lapse_seconds: float) -> None:
        self.store.execute("INSERT INTO leases (name, device_id, account_id, renewed_at, lapse_seconds) VALUES (?, ?, ?, ?, ?) ON CONFLICT (name) DO UPDATE SET device_id = excluded.device_id, account_id = excluded.account_id, renewed_at = excluded.renewed_at, lapse_seconds = excluded.lapse_seconds", (name, device_id, account_id, renewed_at, lapse_seconds))

    def remove(self, name: str) -> None:
        self.store.execute("DELETE FROM leases WHERE name = ?", (name,))

    def remove_person(self, account_id: int) -> None:
        self.store.execute("DELETE FROM leases WHERE account_id = ?", (account_id,))
