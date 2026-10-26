import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.db.migrations.sequence_step_records import step_records

# the name the sequence state is stored under in an agent's stack, frozen here as it was when the runs moved onto the stack
FOLLOWING_SEQUENCE = "following_sequence"
RUN_FIELDS = {"suspension_reason": "pause_reason"}
# the states that pop on an event of their own and take no push, frozen here by their stored names: the runs go beneath them
PUSH_REFUSING = ("awaiting", "stuck", "limited", "waiting", "paused", "compacting", "reading_overview", "demand_block", "ended")


class SequenceRunsStacked(Migration):
    """Each run kept on an agent's row becomes a sequence state on its stack, beneath any wait, compaction, overview or end on top of it, the oldest run lowest and the run in hand highest, its steps records and its pause reason under its present name; the runs column is then dropped, since the stack is where a run lives now."""

    number: ClassVar[int] = 68

    def apply(self, connection: Connection) -> None:
        if not self.has_table(connection, "agents") or "sequence_runs" not in {row["name"] for row in connection.all("PRAGMA table_info(agents)")}:
            return
        for row in connection.all("SELECT id, stack, sequence_runs FROM agents WHERE sequence_runs IS NOT NULL AND sequence_runs != '[]' AND sequence_runs != ''"):
            layers = [{"state": FOLLOWING_SEQUENCE, "data": {"run": stacked_run(run)}} for run in json.loads(row["sequence_runs"])]
            connection.execute("UPDATE agents SET stack = ? WHERE id = ?", (json.dumps(stacked(json.loads(row["stack"] or "[]"), layers)), row["id"]))
        connection.execute("ALTER TABLE agents DROP COLUMN sequence_runs")


def stacked_run(run: dict) -> dict:
    return {**{RUN_FIELDS.get(key, key): value for key, value in run.items()}, "steps": step_records(run.get("steps", []))}


def stacked(stack: list[dict], layers: list[dict]) -> list[dict]:
    floor = len(stack)
    while floor and stack[floor - 1].get("state") in PUSH_REFUSING:
        floor -= 1
    return [*stack[:floor], *layers, *stack[floor:]]
