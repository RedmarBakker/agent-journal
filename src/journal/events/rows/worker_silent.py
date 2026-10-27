from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_mention import WorkerMention


@dataclass(frozen=True, kw_only=True)
class WorkerSilent(RowEvent):
    """A running worker has said nothing for its span, or for twice its span when the work should be split: told once to the agent that dispatched it."""

    feature_name = "workers"

    worker: WorkerMention
    minutes: int
    is_split_due: bool
