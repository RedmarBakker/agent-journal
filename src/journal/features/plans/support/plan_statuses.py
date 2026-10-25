from journal.features.plans.support.plan_status import PlanStatus
from journal.models.plan import Plan
from journal.repositories.plans import Plans


class PlanStatuses:
    """The status of every started plan, oldest first."""

    def __init__(self, plans: Plans) -> None:
        self.plans = plans

    def started(self) -> tuple[PlanStatus, ...]:
        return tuple(self.status(plan) for plan in sorted(self.plans.running_plans(), key=lambda plan: plan.row_id))

    def status(self, plan: Plan) -> PlanStatus:
        phases = self.plans.phase_states(plan)
        total = self.plans.task_count(plan)
        return PlanStatus(plan.row_id, plan.title, plan.current_phase(phases) if phases else 0, len(phases), total - self.plans.remaining_count(plan), total, self.plans.unassigned_count(plan), self.plans.last_moved(plan))
