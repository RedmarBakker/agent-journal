from journal.features.plans.support.plan_agent_coordinator import PlanAgentCoordinator
from journal.models.plan import Plan
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class PlanFocus:
    """The main agent follows one started plan at a time when Plan agents are off; starting or resuming one pauses every other started plan, and turning Plan agents off keeps the furthest along and pauses the rest."""

    def __init__(self, plans: Plans, coordinator: PlanAgentCoordinator, time_source: TimeSource) -> None:
        self.plans, self.coordinator, self.time_source = plans, coordinator, time_source

    def pause_rest(self, plan_id: int, actor: Actor) -> None:
        if self.coordinator.is_coordinator():
            return
        for started in self.plans.running_plans_beside(plan_id):
            self.plans.save(started.focus_postponed(self.time_source.seconds()), actor)

    def furthest_plan(self, actor: Actor) -> None:
        started_plans = self.plans.running_plans()
        if self.coordinator.is_coordinator() or len(started_plans) < 2:
            return
        self.pause_rest(max(started_plans, key=lambda plan: (self.completed_share(plan), -plan.row_id)).row_id, actor)

    def completed_share(self, plan: Plan) -> float:
        total = self.plans.task_count(plan)
        return (total - self.plans.remaining_count(plan)) / total if total else 0.0

