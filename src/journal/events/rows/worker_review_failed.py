from dataclasses import dataclass

from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerReviewFailed(RowResolved):
    """The journal's reviewer of a clocked-out worker's work ended without a report, so the work waits for the check of the agent that sent the worker."""

    feature_name = "workers"

    worker: WorkerMention
    task: int
