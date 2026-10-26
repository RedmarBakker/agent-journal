from dataclasses import dataclass

from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerReviewUndecided(RowResolved):
    """The journal's reviewer could not decide a point of a clocked-out worker's work, so the agent that sent the worker decides it."""

    feature_name = "workers"

    worker: WorkerMention
    task: int
    reviewer: int
    report: str
