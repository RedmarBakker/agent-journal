from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskTestFailed(RowEvent):
    """A task waiting in testing is paused for its agent to take up again, because the run that tests it did not pass, with how the run ended."""

    feature_name = "tasks"

    task_id: int
    output_id: int
    outcome: str
