from dataclasses import dataclass

from journal.features.plans.support.plan_status import PlanStatus
from journal.features.plans.support.started_plan import StartedPlan


@dataclass(frozen=True)
class PlansData:
    """The plans feature's reading: the approved plans, the started plan when one is, the status of every started plan, the reports about a plan in review still unread, and the plan the agent paused itself with its tasks."""

    approved: tuple[int, ...]
    started: StartedPlan | None
    started_plans: tuple[PlanStatus, ...] = ()
    review_reports: tuple[int, ...] = ()
    agent_paused_plan: int = 0
    agent_paused_tasks: tuple[int, ...] = ()
