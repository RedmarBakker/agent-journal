import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

DROPPED_COLUMNS = {"tasks": ("pause_reason", "wait_ended_at"), "agents": ("paused_declined",)}
CHOICE_STATE = "choosing_paused_work"


class PauseColumnsDrop(Migration):
    """With paused tasks gone, the columns that held a pause are dropped, the reason, the end of its wait and the agent's choice to set paused work aside, and the choice of paused work leaves every agent's stack."""

    number: ClassVar[int] = 86

    def apply(self, connection: Connection) -> None:
        for table, columns in DROPPED_COLUMNS.items():
            present = {row["name"] for row in connection.all(f"PRAGMA table_info({table})")}
            for column in (column for column in columns if column in present):
                connection.execute(f"ALTER TABLE {table} DROP COLUMN {column}")
        for row in connection.all("SELECT id, stack FROM agents WHERE stack LIKE ?", (f"%{CHOICE_STATE}%",)):
            stack = [layer for layer in json.loads(row["stack"]) if layer["state"] != CHOICE_STATE]
            connection.execute("UPDATE agents SET stack = ?, state = ?, data = ? WHERE id = ?", (json.dumps(stack), stack[-1]["state"], json.dumps(stack[-1]["data"]), row["id"]))
