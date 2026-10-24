from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class DeveloperNumbersDrop(Migration):
    """The developer numbers are kept in the server's memory: the timings table is dropped, and the statistics rows the numbers were written to are removed."""

    number: ClassVar[int] = 43

    def apply(self, connection: Connection) -> None:
        connection.execute("DROP TABLE IF EXISTS timings")
        connection.execute("DELETE FROM statistics WHERE key LIKE 'developer.%'")
