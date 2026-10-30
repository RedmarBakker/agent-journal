from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

SYNC_TABLES = ("outgoing_changes", "id_blocks", "pending_uploads")


class SyncTablesDrop(Migration):
    """The row sync to a team server is gone, so the tables it kept are dropped: the changes waiting to be sent, the blocks of row numbers the server handed out, and the files waiting to be uploaded."""

    number: ClassVar[int] = 84

    def apply(self, connection: Connection) -> None:
        for table in SYNC_TABLES:
            if self.has_table(connection, table):
                connection.execute(f"DROP TABLE {table}")
