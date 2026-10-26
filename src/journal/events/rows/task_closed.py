from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskClosed(RowEvent):
    """A task was closed: done, paused or cancelled, as how says; worker_id names the worker whose merge closed it."""

    feature_name = "tasks"

    task_id: int
    outcome: str
    worker_id: int = 0
