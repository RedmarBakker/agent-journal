from dataclasses import dataclass
from typing import ClassVar

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanReviewStarted(RowEvent):
    """A plan was put into review, so its reviewers can be sent; moment is the name a sequence's trigger gives it."""

    moment: ClassVar[str] = "plan.review_started"
    feature_name = "plans"

    plan_id: int
