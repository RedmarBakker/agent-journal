from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerSentToReview(RowEvent):
    """A worker handed in its work with a proof for each point of its brief, and its report goes to the journal's reviewer rather than to the agent that sent it."""

    worker: WorkerMention
    report: str
