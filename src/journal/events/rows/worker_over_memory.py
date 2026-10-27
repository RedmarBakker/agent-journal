from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerOverMemory(RowEvent):
    """A worker's process tree uses more resident memory than the budget past which the agent that sent it is warned."""

    feature_name = "workers"

    worker: WorkerMention
    megabytes: int
    budget_megabytes: int
