from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskTransferred(RowEvent):
    """A task was moved from this environment to another, its state kept; heard by the agents of the environment it came from."""

    feature_name = "tasks"

    task_id: int
    destination: str
