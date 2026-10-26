from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerTestFailed(RowEvent):
    """A worker's test run failed: how many of its tests failed, and how many of the worker's runs in a row have failed."""

    feature_name = "workers"

    worker: WorkerMention
    failed: int
    runs: int

    def is_streak(self, length: int) -> bool:
        return self.runs == length
