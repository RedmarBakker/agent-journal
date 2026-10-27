import json
from pathlib import Path

from journal.support.schema_node import SchemaNode

SCHEMA = Path(__file__).with_name("command_table.schema.json")


class TableSchema:
    """The command table's schema, read once into nodes: the faults a table holds against it, each named by where it stands, as a type that does not match, a key that is missing or one that is not allowed."""

    def __init__(self) -> None:
        data = json.loads(SCHEMA.read_text())
        self.root = SchemaNode.parsed(data)
        self.definitions = {name: SchemaNode.parsed(node) for name, node in data["$defs"].items()}

    def faults(self, table: dict) -> list[str]:
        return self.root.faults(table, "table", self.definitions)
