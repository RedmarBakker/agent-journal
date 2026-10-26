import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

HELPER_ROLES = ("worker", "verifier", "reviewer", "subagent")


class VoidHelperFloors(Migration):
    """Every helper's stack rests on Void: a worker's duty floor becomes void and its main-agent working layer the worker's own working_task, a reviewer's or verifier's state is kept over a void floor, and a main agent's duty floor becomes idle, which its work mode then replaces."""

    number: ClassVar[int] = 59

    def apply(self, connection: Connection) -> None:
        for row in connection.all("SELECT id, role, state, data, stack FROM agents"):
            stack = json.loads(row["stack"] or "[]") or [{"state": row["state"], "data": json.loads(row["data"] or "{}")}]
            moved = helper_stack(stack) if row["role"] in HELPER_ROLES else main_stack(stack)
            if moved != stack:
                connection.execute("UPDATE agents SET stack = ?, state = ?, data = ? WHERE id = ?", (json.dumps(moved), moved[-1]["state"], json.dumps(moved[-1]["data"]), row["id"]))


def helper_stack(stack: list[dict]) -> list[dict]:
    layers = [{"state": "working_task", "data": {"task_id": layer.get("data", {}).get("task_id", 0)}} if layer["state"] == "working" else layer for layer in stack if layer["state"] != "duty"]
    return layers if layers and layers[0]["state"] == "void" else [{"state": "void", "data": {}}, *layers]


def main_stack(stack: list[dict]) -> list[dict]:
    return [{"state": "idle", "data": {}} if layer["state"] == "duty" else layer for layer in stack]
