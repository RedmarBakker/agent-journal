from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerReviewed(RowEvent):
    """The journal's reviewer reported on a clocked-out worker's work, one line per point of its task's brief: signed off, sent back short, or left for the agent to decide."""

    feature_name = "reviewing"

    worker: WorkerMention
    task: int
    reviewer: int
    reviewer_session: str
    report: str
