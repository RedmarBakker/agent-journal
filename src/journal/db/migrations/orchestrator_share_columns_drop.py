from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

DROPPED_COLUMNS = ("merge_uses", "prepared_merge_uses", "reuse_uses", "fresh_idle_uses", "late_worker_uses", "late_task_uses", "queue_use", "is_proof_read", "test_run_at", "test_run_folder")


class OrchestratorShareColumnsDrop(Migration):
    """The orchestrator's tool-use shares are gone, so the agent columns only they read are dropped: its merges and prepared merges, its sends to idle workers and fresh dispatches over them, the tool uses made while a worker or a task waited, its queue use, and the proof read and test run a prepared merge looked for."""

    number: ClassVar[int] = 61

    def apply(self, connection: Connection) -> None:
        present = {row["name"] for row in connection.all("PRAGMA table_info(agents)")}
        for column in (column for column in DROPPED_COLUMNS if column in present):
            connection.execute(f"ALTER TABLE agents DROP COLUMN {column}")
