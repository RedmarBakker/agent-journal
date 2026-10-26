from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReviewerEnded(RowEvent):
    """A reviewer's run ended, or ran past its limit, before it gave its report, so it leaves the reviewers and the next review goes to another."""

    feature_name = "reviewing"
