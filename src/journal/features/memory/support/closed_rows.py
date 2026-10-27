from journal.features.mentions.support.mention_match import MentionMatch
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.repositories.rows import Rows

CLOSED_STATES = {
    "tasks": {TaskState.COMPLETED, TaskState.CANCELLED},
    "plans": {PlanState.FINISHED, PlanState.CANCELLED},
    "workers": {WorkerState.STOPPED, WorkerState.RELEASED, WorkerState.MERGED},
}


class ClosedRows:
    """The rows a memory's text names that are closed since it was written: a task or plan done or cancelled, a worker stopped, released or merged, or any named row that is not found, each said as its noun, number and state."""

    def __init__(self, rows: Rows) -> None:
        self.rows = rows

    def described(self, text: str) -> list[str]:
        return [f"{ref.type.removesuffix('s')} {ref.id} {state}" for ref in MentionMatch.found(text) if (state := self.closed_state(ref.type, self.rows.is_row(ref), self.rows.row_state(ref)))]

    @staticmethod
    def closed_state(table: str, exists: bool, state: str) -> str:
        if not exists:
            return "not found"
        return state if state in CLOSED_STATES.get(table, set()) else ""
