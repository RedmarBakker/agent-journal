from datetime import datetime, timezone
from journal.models.plan import Plan
from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.support.actor import Actor
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.repositories.plans import Plans
from journal.features.plans.plans_nudges import PlansNudges
from journal.support.time_source import TimeSource

BLOCKABLE_STATES = (PlanState.STARTED, PlanState.PAUSED, PlanState.DELEGATED)


class PlanBlockade(Listener[Updated]):
    """A started, paused or delegated plan whose every remaining task is blocked blocks itself, done with all but those, since none of its work can continue, and opens again the moment one of them opens; a single blocked task never blocks its plan. The agent is informed either way."""

    def __init__(self, plans: Plans, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.plans = plans

    def handle(self, event: Updated) -> None:
        task, previous = event.model, event.previous_row(Task)
        if not isinstance(task, Task) or previous is None or task.state == previous.state:
            return
        for plan in self.plans.containing(task):
            if plan.state in BLOCKABLE_STATES and self.plans.is_stalled(plan):
                self.plans.save(plan.blocked(PlansNudges.ALL_BLOCKED, self.time_source.moment().timestamp()), Actor.system())
            elif self.is_unblockable(plan):
                self.plans.save(plan.unblocked(f"task {task.id} is open again", self.time_source.moment().timestamp()), Actor.system())

    def is_unblockable(self, plan: Plan) -> bool:
        return plan.is_blocked() and plan.block_reason == PlansNudges.ALL_BLOCKED and not self.plans.is_stalled(plan)
