import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class SequenceStepRecords(Migration):
    """Every sequence's stored steps become records, its title, its instructions and its guards: a step stored as a plain string becomes its instructions with file edits allowed; the record's shape is frozen here as it was when steps became records."""

    number: ClassVar[int] = 67

    def apply(self, connection: Connection) -> None:
        if not self.has_table(connection, "sequences"):
            return
        for row in connection.all("SELECT id, steps FROM sequences"):
            connection.execute("UPDATE sequences SET steps = ? WHERE id = ?", (json.dumps(step_records(json.loads(row["steps"] or "[]"))), row["id"]))


def step_records(steps: list) -> list[dict]:
    return [step_record(step) for step in steps]


def step_record(step: dict | str) -> dict:
    if isinstance(step, str):
        return {"title": "", "instructions": step, "file_edits_allowed": True, "allowed_commands": [], "ending_moment": ""}
    return {"title": str(step.get("title", "")), "instructions": str(step.get("instructions", "")), "file_edits_allowed": bool(step.get("file_edits_allowed", True)), "allowed_commands": list(step.get("allowed_commands", [])), "ending_moment": str(step.get("ending_moment", ""))}
