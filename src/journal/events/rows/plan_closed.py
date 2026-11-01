from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanClosed(RowEvent):
    """A plan was cancelled or finished."""

    feature_name = "plans"

    plan_id: int
