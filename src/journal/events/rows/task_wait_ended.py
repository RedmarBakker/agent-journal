from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TaskWaitEnded(RowEvent):
    """What a paused task waited on arrived, with the reason as a clause: task 12 it waited on is done. The task stays paused until it is resumed."""

    task_id: int
    reason: str
