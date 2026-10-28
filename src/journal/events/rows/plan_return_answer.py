from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanReturnAnswer(RowEvent):
    """The agent said whether it returns to the plan it paused once the task it took up outside the plan is done."""

    feature_name = "plans"

    plan_id: int
    returning: bool
