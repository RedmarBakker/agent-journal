from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class CheckFailed(RowEvent):
    """A check ran and failed."""

    check_id: int
