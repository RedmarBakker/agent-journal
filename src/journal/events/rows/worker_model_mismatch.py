from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerModelMismatch(RowEvent):
    """A worker's merged work did not fit the model it ran on: too strong or too weak, the model, how complex the work measured, and how many times it was sent back."""

    worker: WorkerMention
    fit: str
    model: str
    points: float
    rejections: int
