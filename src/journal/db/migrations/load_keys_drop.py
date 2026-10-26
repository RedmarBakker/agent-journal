from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

REMOVED_KEYS = ("over_full_minutes", "over_zero_minutes")
MODES = ("builder", "orchestrator", "solo")


class LoadKeysDrop(Migration):
    """The keys the agent's stored loads kept for the minutes over the level its fitness once counted are removed from its queues and its loads by mode, so a load written before they went still reads."""

    number: ClassVar[int] = 64

    def apply(self, connection: Connection) -> None:
        queue_paths = ", ".join(f"'$.{key}'" for key in REMOVED_KEYS)
        mode_paths = ", ".join(f"'$.{mode}.{key}'" for mode in MODES for key in REMOVED_KEYS)
        for column in ("work_queue", "message_queue"):
            connection.execute(f"UPDATE agents SET {column} = json_remove({column}, {queue_paths}) WHERE json_valid({column})")
        connection.execute(f"UPDATE agents SET mode_loads = json_remove(mode_loads, {mode_paths}) WHERE json_valid(mode_loads)")
