import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.models.supervisor_grant import SupervisorGrant


class SupervisorGrantsVersionTwo(Migration):
    """Every version one supervisor grant carries its version two environment scope and permissions."""

    number: ClassVar[int] = 91

    def apply(self, connection: Connection) -> None:
        rows = connection.all("SELECT id, data FROM entries WHERE entry_type = 'SupervisorGrant'")
        for row in rows:
            data = json.loads(row["data"] or "{}")
            if "grant_v2" in data:
                continue
            data["grant_v2"] = SupervisorGrant.from_version_one(data).data()
            connection.execute("UPDATE entries SET data = ? WHERE id = ?", (json.dumps(data), row["id"]))
