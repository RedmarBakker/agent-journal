from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanReopened(RowEvent):
    """A blocked or finished plan was opened again, with the reason: unblocked, or work added to it."""

    feature_name = "plans"

    plan_id: int
    reason: str
