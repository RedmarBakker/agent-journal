from dataclasses import dataclass

from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerReviewed(RowResolved):
    """The journal's reviewer reported on a clocked-out worker's work, one line per point of its task's brief, with the tests it ran."""

    worker: WorkerMention
    task: int
    reviewer: int
    reviewer_session: str
    report: str
