from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskStarted(RowEvent):
    """A task was started, from the state it stood in before: open, or paused when a paused task is resumed."""

    feature_name = "tasks"

    task_id: int
    title: str
    plan_id: int
    prior_state: str = ""
