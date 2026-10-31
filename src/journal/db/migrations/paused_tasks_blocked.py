from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class PausedTasksBlocked(Migration):
    """A task is no longer paused: every paused task becomes blocked, its pause reason kept as its block reason and
    its waits kept as they are."""

    number: ClassVar[int] = 85

    def apply(self, connection: Connection) -> None:
        present = {row["name"] for row in connection.all("PRAGMA table_info(tasks)")}
        reason = "CASE WHEN pause_reason != '' THEN pause_reason ELSE 'paused before version 4.69.15' END" if "pause_reason" in present else "'paused before version 4.69.15'"
        connection.execute(f"UPDATE tasks SET state = 'blocked', block_reason = {reason} WHERE state = 'paused'")
