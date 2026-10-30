from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class EnvironmentKinds(Migration):
    """Every environment made before environments had a kind is a local one, of no team, while those columns stood."""

    number: ClassVar[int] = 51

    def apply(self, connection: Connection) -> None:
        columns = self.column_names(connection, "environments")
        if "kind" in columns:
            connection.execute("UPDATE environments SET kind = 'local' WHERE kind IS NULL")
        if "team_key" in columns:
            connection.execute("UPDATE environments SET team_key = '' WHERE team_key IS NULL")
