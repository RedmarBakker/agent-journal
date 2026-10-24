from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.features.plans.states.plan_work import PlanWork
from journal.features.plans.states.following_plan import FollowingPlan


@dataclass(frozen=True)
class PlansWorking(PlanWork):
    """On one task with plans on: its plan state is FollowingPlan."""

    def plan_state(self, **fields) -> BaseState:
        return FollowingPlan(**fields)
