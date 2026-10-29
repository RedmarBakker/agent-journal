from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskArrived(RowEvent):
    """A task was moved into this environment from another, in the state it had there; heard by the agents it came to."""

    feature_name = "tasks"

    task_id: int
    title: str
    source: str
    state: str
