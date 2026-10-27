from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

FACT_WEIGHT = 5


class FactMemories(Migration):
    """Every fact still standing becomes a memory of weight 5 in its environment, with its text, keywords and times; a fact whose text is already a memory there is passed over, so a second run adds nothing."""

    number: ClassVar[int] = 72

    def apply(self, connection: Connection) -> None:
        if not self.has_table(connection, "facts") or not self.has_table(connection, "memories"):
            return
        connection.execute(
            "INSERT INTO memories (created_at, creator, updated_at, updater, environment_id, text, weight, keywords) "
            "SELECT created_at, creator, updated_at, updater, environment_id, text, ?, keywords FROM facts "
            "WHERE NOT EXISTS (SELECT 1 FROM memories WHERE memories.environment_id = facts.environment_id AND memories.text = facts.text) ORDER BY id",
            (FACT_WEIGHT,),
        )
