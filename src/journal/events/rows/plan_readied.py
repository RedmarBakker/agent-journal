from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanReadied(RowEvent):
    """A plan was marked ready for the user to approve."""

    feature_name = "plans"

    plan_id: int
