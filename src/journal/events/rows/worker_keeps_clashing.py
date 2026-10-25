from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerKeepsClashing(RowEvent):
    """A worker's branch was sent back to rebase as many times in a row as the setting allows, merges landing faster than it can follow: how many times, and the files it clashes in now."""

    worker: WorkerMention
    clashes: int
    clashing: str
