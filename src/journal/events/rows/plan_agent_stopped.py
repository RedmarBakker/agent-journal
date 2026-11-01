from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanAgentStopped(RowEvent):
    """A plan ended and its Plan agent's work stack is cleared."""

    feature_name = "plans"

    plan_id: int
