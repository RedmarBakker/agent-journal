from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskEdited(RowEvent):
    """A task's title or brief was written anew: changes names which of the two changed, and points the brief's points whose wording changed or that are new."""

    feature_name = "tasks"

    task_id: int
    changes: tuple[str, ...]
    points: tuple[int, ...] = ()
