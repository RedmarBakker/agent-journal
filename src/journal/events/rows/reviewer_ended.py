from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReviewerEnded(RowEvent):
    """A reviewer's run ended, or ran past its limit, before it gave its report."""
