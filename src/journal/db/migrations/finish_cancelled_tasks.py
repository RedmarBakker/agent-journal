from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class FinishCancelledTasks(Migration):
    """A task cancelled before a cancel stamped when it finished takes its last change as its finish, so no count takes it for open."""

    number: ClassVar[int] = 2

    def apply(self, connection: Connection) -> None:
        column = "finished_at" if any(row["name"] == "finished_at" for row in connection.all("PRAGMA table_info(tasks)")) else "completed_at"
        connection.execute(f"UPDATE tasks SET {column} = updated_at WHERE state = 'cancelled' AND {column} IS NULL")
