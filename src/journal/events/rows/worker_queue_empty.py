from dataclasses import dataclass

from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerQueueEmpty(RowResolved):
    """A worker's work was merged and nothing waits in its queue, so it has no work left."""

    worker: WorkerMention
