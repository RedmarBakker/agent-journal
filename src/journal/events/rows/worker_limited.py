from dataclasses import dataclass

from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerLimited(RowResolved):
    """A worker's run ended on the provider's usage limit: it waits, holding its task, until the time it resumes, when the limit resets and it is sent on in its own session."""

    worker: WorkerMention
    resumes_at: float
