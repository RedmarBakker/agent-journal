from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class BrowserSessionsDrop(Migration):
    """The hosted journal and its browser sign-in are gone, so the table of signed-in browsers is dropped."""

    number: ClassVar[int] = 81

    def apply(self, connection: Connection) -> None:
        if self.has_table(connection, "browser_sessions"):
            connection.execute("DROP TABLE browser_sessions")
