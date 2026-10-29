from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanApproved(RowEvent):
    """A plan was approved, by the user or by a command, and the number of the comment the user approved it with, if any."""

    feature_name = "plans"

    plan_id: int
    user_origin: bool
    comment_id: int | None = None
