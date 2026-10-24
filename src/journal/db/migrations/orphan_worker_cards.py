from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

# a chat card names its worker by its row, workers:12, or by its key, worker:12 and what follows
ORPHAN_CONDITION = ("(json_extract(data, '$.row') LIKE 'workers:%' AND CAST(substr(json_extract(data, '$.row'), 9) AS INTEGER) NOT IN (SELECT id FROM workers))"
                    " OR (json_extract(data, '$.key') LIKE 'worker:%' AND CAST(substr(json_extract(data, '$.key'), 8) AS INTEGER) NOT IN (SELECT id FROM workers))")


class OrphanWorkerCards(Migration):
    """The chat cards of the verifiers once kept as workers, whose rows migration 48 removed, go too, so the chat never opens a worker that is not there; a journal whose workers already moved to the table of sent agents has none left."""

    number: ClassVar[int] = 49

    def apply(self, connection: Connection) -> None:
        if self.has_table(connection, "workers"):
            connection.execute(f"DELETE FROM messages WHERE {ORPHAN_CONDITION}")
