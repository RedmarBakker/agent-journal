from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class CheckFailed(RowEvent):
    """A check ran and failed."""

    feature_name = "checks"

    check_id: int
