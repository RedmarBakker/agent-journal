from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class TimedLineSeries(Migration):
    """The agent's line series turn from pairs keyed by a tool use's number into pairs keyed by a time in seconds: the old pairs mean nothing as times, so they are cleared and the series start empty."""

    number: ClassVar[int] = 60

    def apply(self, connection: Connection) -> None:
        connection.execute("UPDATE agents SET edited_lines = '[]', merged_lines = '[]'")
