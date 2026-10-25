from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerQueueTurnEnded(RowEvent):
    """A worker's process ended mid-queue, after it had moved on to the next task of its queue and before it clocked out of it: it is sent on in its own session with that task, with no report and no merge."""

    worker: WorkerMention
    task: int
