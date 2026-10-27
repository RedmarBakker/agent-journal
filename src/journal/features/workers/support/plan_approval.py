from enum import StrEnum

from journal.models.plan import Plan
from journal.support.actor import Actor


class PlanApproval(StrEnum):
    """Which plans the orchestrator may approve itself while the user lets it approve plans: only those a main agent created, so its own across sessions, those the user created, or all."""

    OWN = "can approve only its own plans"
    USER_MADE = "can approve plans the user made"
    ALL = "can approve all plans"

    def allows(self, plan: Plan, approver: Actor) -> bool:
        return self is PlanApproval.ALL or (self is PlanApproval.OWN and plan.creation_actor.actor_type == approver.actor_type) or (self is PlanApproval.USER_MADE and plan.creation_actor.is_user())
