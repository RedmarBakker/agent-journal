from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanDelegated(RowEvent):
    """A plan's work went to workers alone: a worker works one of its tasks and its agent holds none, so it is no longer the agent's active plan."""

    feature_name = "plans"

    plan_id: int
