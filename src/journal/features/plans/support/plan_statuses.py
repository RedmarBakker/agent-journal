from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.plans.support.plan_status import PlanStatus
from journal.models.plan import Plan
from journal.repositories.plans import Plans


class PlanStatuses:
    """The status of every started plan, oldest first, including whether its Plan agent runs."""

    def __init__(self, plans: Plans, agents: PlanAgents) -> None:
        self.plans, self.agents = plans, agents

    def started(self) -> tuple[PlanStatus, ...]:
        return tuple(self.status(plan) for plan in sorted(self.plans.running_plans(), key=lambda plan: plan.row_id))

    def status(self, plan: Plan) -> PlanStatus:
        phases = self.plans.phase_states(plan)
        total = self.plans.task_count(plan)
        return PlanStatus(
            plan_id=plan.row_id,
            title=plan.title,
            phase=plan.current_phase(phases) if phases else 0,
            phases=len(phases),
            done=total - self.plans.remaining_count(plan),
            total=total,
            unassigned=self.plans.unassigned_count(plan),
            moved_at=self.plans.last_moved(plan),
            blocked=self.plans.blocked_count(plan),
            agent_running=self.agent_is_running(plan),
        )

    def agent_is_running(self, plan: Plan) -> bool:
        if not self.agents.is_on():
            return False
        environment = self.agents.environment(plan)
        return bool(environment and self.agents.is_running(environment))
