from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

STATE_UPDATES = ("UPDATE tasks SET state = 'paused' WHERE state = 'parked'", "UPDATE plans SET state = 'paused' WHERE state = 'parked'")


class PausedTasks(Migration):
    """A task or plan set aside is paused, no longer parked or suspended: its stored state and the column with its reason take the new word."""

    number: ClassVar[int] = 42

    def apply(self, connection: Connection) -> None:
        self.column_rename(connection, "tasks", "suspension_reason", "pause_reason")
        for statement in STATE_UPDATES:
            connection.execute(statement)
