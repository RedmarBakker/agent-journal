from journal.features.workers.support.orchestrator_mode import OrchestratorMode
from journal.models.plan import Plan
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class PlanFocus:
    """A builder or a solo agent follows one started plan at a time: starting or resuming one pauses every other started plan, and a switch out of the orchestrator mode keeps the plan furthest along, the oldest when two are even, and pauses the rest; an orchestrator keeps all its started plans."""

    def __init__(self, plans: Plans, orchestrator: OrchestratorMode, time_source: TimeSource) -> None:
        self.plans, self.orchestrator, self.time_source = plans, orchestrator, time_source

    def pause_rest(self, plan_id: int, actor: Actor) -> None:
        if self.orchestrator.is_set():
            return
        for started in self.plans.running_plans_beside(plan_id):
            self.plans.save(started.postponed(self.time_source.seconds(), False), actor)

    def keep_furthest(self, actor: Actor) -> None:
        started_plans = self.plans.running_plans()
        if self.orchestrator.is_set() or len(started_plans) < 2:
            return
        self.pause_rest(max(started_plans, key=lambda plan: (self.completed_share(plan), -plan.row_id)).row_id, actor)

    def completed_share(self, plan: Plan) -> float:
        total = self.plans.task_count(plan)
        return (total - self.plans.remaining_count(plan)) / total if total else 0.0
