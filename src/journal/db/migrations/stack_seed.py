import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.db.migrations.stored_state import StoredState

IDLE = "idle"


class StackSeed(Migration):
    """Every agent's row gets its stack, built from its state and data: a pause's resume chain sits below it, unwound into one entry per state, with idle at the bottom; the state and data stay those of the top entry."""

    number: ClassVar[int] = 18

    def apply(self, connection: Connection) -> None:
        for row in connection.all("SELECT id, state, data FROM agents"):
            stored = StoredState.parsed(row["state"], json.loads(row["data"] or "{}"))
            connection.execute("UPDATE agents SET stack = ? WHERE id = ?", (json.dumps(self.stack(stored)), row["id"]))

    @staticmethod
    def stack(stored: StoredState) -> list[dict]:
        layers = [stored]
        while layers[-1].resume:
            layers.append(layers[-1].resume)
        if layers[-1].name != IDLE:
            layers.append(StoredState(IDLE, {}))
        return [{"state": layer.name, "data": layer.data} for layer in reversed(layers)]
