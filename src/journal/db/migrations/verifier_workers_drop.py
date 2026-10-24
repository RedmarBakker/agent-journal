from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class VerifierWorkersDrop(Migration):
    """A verifier is an agent of its own now, never a worker: the verifiers once kept as workers go, with their links to the reports they judged, and the workers table loses the role column that told them apart."""

    number: ClassVar[int] = 48

    def apply(self, connection: Connection) -> None:
        if "role" not in {row["name"] for row in connection.all("PRAGMA table_info(workers)")}:
            return
        connection.execute("DELETE FROM links WHERE kind = 'verifies' AND source IN (SELECT 'workers:' || id FROM workers WHERE role = 'verifier')")
        connection.execute("DELETE FROM workers WHERE role = 'verifier'")
        connection.execute("ALTER TABLE workers DROP COLUMN role")
