from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

DROPPED_COLUMNS = ("consecutive_handovers", "last_handover_at", "subagent_dispatch_uses", "research_uses", "handover_uses", "file_edit_uses", "task_filed_uses", "task_completed_uses", "briefed_uses", "mode_started_use", "fitness_level", "report_use")


class ToolUseColumnsDrop(Migration):
    """The fitness is worked out from the measures alone, so the agent columns the old tool-use score read are dropped, with the fitness level it was told at and the report use its point drops kept, and the load level entries its load lines read are deleted."""

    number: ClassVar[int] = 62

    def apply(self, connection: Connection) -> None:
        present = {row["name"] for row in connection.all("PRAGMA table_info(agents)")}
        for column in (column for column in DROPPED_COLUMNS if column in present):
            connection.execute(f"ALTER TABLE agents DROP COLUMN {column}")
        connection.execute("DELETE FROM entries WHERE kind = 'workload_level'")
