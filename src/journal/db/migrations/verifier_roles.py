from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class VerifierRoles(Migration):
    """A verifier sent before a worker's row named its role takes the verifier's role, found by its link to the row it judged; a journal whose workers no longer have a role column has nothing to do."""

    number: ClassVar[int] = 45

    def apply(self, connection: Connection) -> None:
        if "role" in {row["name"] for row in connection.all("PRAGMA table_info(workers)")}:
            connection.execute("UPDATE workers SET role = 'verifier' WHERE 'workers:' || id IN (SELECT source FROM links WHERE kind = 'verifies')")
