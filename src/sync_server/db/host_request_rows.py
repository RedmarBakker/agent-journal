from dataclasses import fields
from sqlite3 import Row

from sync_server.db.store import Store
from sync_server.host_request_draft import HostRequestDraft
from sync_server.request_audience import RequestAudience

COLUMNS = "id, environment_key, kind, body, account_id, created_at, audience, device_id, version"


class HostRequestRows:
    """The SQL of the host_requests table: a write asked of another machine, waiting until a machine has made it, then naming who made it; a pool request is claimed by one machine, and a machine that declines one is not offered it again."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def insert(self, draft: HostRequestDraft) -> int:
        return self.store.insert("host_requests", {field.name: getattr(draft, field.name) for field in fields(draft)})

    def waiting(self, device_id: int, environment_keys: tuple[str, ...], pool_free: int, version: str) -> list[Row]:
        placeholders = ", ".join("?" for _ in environment_keys) or "NULL"
        return self.store.all(
            f"SELECT {COLUMNS} FROM host_requests WHERE finished_at = 0 AND claimed_by = 0 AND NOT EXISTS (SELECT 1 FROM json_each(declined) WHERE value = ?) "
            f"AND ((audience = ? AND environment_key IN ({placeholders})) OR (audience = ? AND device_id = ?) OR (audience = ? AND ? > 0 AND version = ?)) ORDER BY id",
            (device_id, RequestAudience.HOST, *environment_keys, RequestAudience.DEVICE, device_id, RequestAudience.POOL, pool_free, version),
        )

    def claim(self, id: int, device_id: int) -> bool:
        return self.store.execute("UPDATE host_requests SET claimed_by = ? WHERE id = ? AND claimed_by = 0 AND finished_at = 0", (device_id, id)).rowcount == 1

    def decline(self, id: int, device_id: int) -> None:
        self.store.execute("UPDATE host_requests SET claimed_by = 0, declined = json_insert(declined, '$[#]', ?) WHERE id = ?", (device_id, id))

    def unclaimed_pool(self, deadline_at: float) -> list[Row]:
        return self.store.all(f"SELECT {COLUMNS} FROM host_requests WHERE audience = ? AND claimed_by = 0 AND finished_at = 0 AND created_at < ? ORDER BY id", (RequestAudience.POOL, deadline_at))

    def claimed_by_quiet_devices(self, pulled_before: float) -> list[Row]:
        columns = ", ".join(f"host_requests.{column.strip()}" for column in COLUMNS.split(","))
        return self.store.all(f"SELECT {columns} FROM host_requests JOIN devices ON devices.id = host_requests.claimed_by WHERE host_requests.audience = ? AND host_requests.finished_at = 0 AND devices.pulled_at < ? ORDER BY host_requests.id", (RequestAudience.POOL, pulled_before))

    def finish(self, id: int, host_id: int, finished_at: float) -> None:
        self.store.execute("UPDATE host_requests SET host_id = ?, finished_at = ? WHERE id = ?", (host_id, finished_at, id))

    def is_vouched(self, host_id: int, account_id: int) -> bool:
        return self.store.one("SELECT 1 FROM host_requests WHERE host_id = ? AND account_id = ? LIMIT 1", (host_id, account_id)) is not None
