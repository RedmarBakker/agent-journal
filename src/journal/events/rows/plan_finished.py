from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.models.plan_mode import PlanMode


@dataclass(frozen=True, kw_only=True)
class PlanFinished(RowEvent):
    """A plan finished, with its work mode."""

    feature_name = "plans"

    plan_id: int
    mode: PlanMode
