import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

FACT_CARDS = "facts"
MEMORY_CARDS = "memories"


class FactTableDrop(Migration):
    """Every card that opened a fact opens the memory migration 72 made of it, shown as a memory card, and the facts table goes; a card whose fact had no memory keeps its words and opens nothing."""

    number: ClassVar[int] = 73

    def apply(self, connection: Connection) -> None:
        if not self.has_table(connection, FACT_CARDS) or not self.has_table(connection, MEMORY_CARDS):
            return
        memory_numbers = {row["fact_id"]: row["memory_id"] for row in connection.all("SELECT facts.id AS fact_id, MIN(memories.id) AS memory_id FROM facts JOIN memories ON memories.environment_id = facts.environment_id AND memories.text = facts.text GROUP BY facts.id")}
        for row in connection.all("SELECT id, text, data FROM messages WHERE json_extract(data, '$.shows') = ? OR json_extract(data, '$.row') LIKE 'facts:%'", (FACT_CARDS,)):
            data = json.loads(row["data"])
            kind, _, number = str(data.get("row", "")).partition(":")
            memory_number = memory_numbers.get(int(number)) if kind == FACT_CARDS and number.isdigit() else None
            if memory_number is None:
                data.pop("row", None)
            else:
                data["row"] = f"{MEMORY_CARDS}:{memory_number}"
            data["shows"] = MEMORY_CARDS
            text = row["text"].replace(f"Fact {number} ", f"Memory {memory_number} ", 1) if memory_number is not None else row["text"]
            connection.execute("UPDATE messages SET text = ?, data = ? WHERE id = ?", (text, json.dumps(data), row["id"]))
        connection.execute("DROP TABLE facts")
