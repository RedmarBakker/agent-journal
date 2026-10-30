from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

WORKER_COLUMNS = ("pool_request", "base", "device")
POOL_SETTINGS = ("workers.pool_slots", "workers.pool_daily_minutes", "workers.pool_profiles")


class PoolDrop(Migration):
    """The team's worker pool is gone, so its jobs table, the worker columns that named a pool request, its base branch and the machine that ran it, and its settings are dropped."""

    number: ClassVar[int] = 78

    def apply(self, connection: Connection) -> None:
        if self.has_table(connection, "pool_jobs"):
            connection.execute("DROP TABLE pool_jobs")
        present = {row["name"] for row in connection.all("PRAGMA table_info(workers)")}
        for column in (column for column in WORKER_COLUMNS if column in present):
            connection.execute(f"ALTER TABLE workers DROP COLUMN {column}")
        connection.execute(f"DELETE FROM settings WHERE key IN ({', '.join('?' for _ in POOL_SETTINGS)})", POOL_SETTINGS)
