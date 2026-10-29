from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class EnvironmentTeams(Migration):
    """The flags that once marked the Team chat and a shared environment are dropped, and every document and revision from before documents had an environment is the project's, in environment 0."""

    number: ClassVar[int] = 52

    def apply(self, connection: Connection) -> None:
        columns = self.column_names(connection, "environments")
        for column in ("is_team_chat", "is_shared_with_team"):
            if column in columns:
                connection.execute(f"ALTER TABLE environments DROP COLUMN {column}")
        for table in ("docs", "doc_revisions"):
            connection.execute(f"UPDATE {table} SET environment_id = 0 WHERE environment_id IS NULL")
