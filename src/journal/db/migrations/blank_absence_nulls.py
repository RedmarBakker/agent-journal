from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class BlankAbsenceNulls(Migration):
    """An agent that has not worked in a mode yet and a memory that ends with no row hold NULL: the blank they were saved with before is NULL."""

    number: ClassVar[int] = 76

    def apply(self, connection: Connection) -> None:
        if self.has_table(connection, "agents"):
            connection.execute("UPDATE agents SET mode = NULL WHERE mode = ''")
        if self.has_table(connection, "memories"):
            connection.execute("UPDATE memories SET expiry_row = NULL WHERE expiry_row = ''")
