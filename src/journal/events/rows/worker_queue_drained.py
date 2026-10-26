from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerQueueDrained(RowEvent):
    """The tasks waiting in a worker's queue were given back, open again."""

    feature_name = "workers"

    worker: WorkerMention
    tasks: str
