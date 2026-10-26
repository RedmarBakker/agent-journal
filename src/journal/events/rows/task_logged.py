from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskLogged(RowEvent):
    """A line was logged on a task."""

    feature_name = "tasks"

    task_id: int
