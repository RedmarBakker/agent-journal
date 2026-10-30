from dataclasses import dataclass

from journal.features.plans.support.plan_status import PlanStatus
from journal.features.plans.support.plan_agent_write_scope import PlanAgentWriteScope
from journal.features.plans.support.started_plan import StartedPlan


@dataclass(frozen=True)
class PlansData:
    """The plans feature's reading: approved and started plans, their reports and statuses, the plan the agent paused itself with its tasks, and a Plan agent's write scope when one is running."""

    approved: tuple[int, ...]
    started: StartedPlan | None
    started_plans: tuple[PlanStatus, ...] = ()
    review_reports: tuple[int, ...] = ()
    agent_paused_plan: int = 0
    agent_paused_tasks: tuple[int, ...] = ()
    plan_agent_write_scope: PlanAgentWriteScope | None = None
