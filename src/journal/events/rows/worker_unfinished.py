from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_resolved import RowResolved


@dataclass(frozen=True, kw_only=True)
class WorkerUnfinished(RowResolved):
    """A worker's run ended without its clocking out: never clocked in, died or ran out of time; its task stays assigned to it."""

    worker: WorkerMention
    times: int = 1
    has_session: bool = False
    is_run_limit: bool = False
