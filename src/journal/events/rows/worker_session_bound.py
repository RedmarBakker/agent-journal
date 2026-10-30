from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerSessionBound(RowEvent):
    """A worker whose provider names its session only at its first hook got its session."""

    feature_name = "workers"
