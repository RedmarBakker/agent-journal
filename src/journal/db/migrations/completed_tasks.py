from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class CompletedTasks(Migration):
    """A task that ended is completed, no longer finished or done: its stored state and the column with its time take the new word."""

    number: ClassVar[int] = 56

    def apply(self, connection: Connection) -> None:
        self.column_rename(connection, "tasks", "finished_at", "completed_at")
        connection.execute("UPDATE tasks SET state = 'completed' WHERE state = 'done'")
