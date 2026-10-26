from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanReopened(RowEvent):
    """A blocked plan was opened again, with the reason it was unblocked."""

    feature_name = "plans"

    plan_id: int
    reason: str
