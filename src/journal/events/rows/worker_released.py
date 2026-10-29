from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_resolved import RowResolved


@dataclass(frozen=True, kw_only=True)
class WorkerReleased(RowResolved):
    """A worker's task was let go without its work being merged, which ends a wait on the worker."""

    feature_name = "workers"

    worker: WorkerMention
