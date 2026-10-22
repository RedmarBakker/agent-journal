from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerReady(RowEvent):
    """A worker reported that it is ready and started its task."""

    worker: WorkerMention
