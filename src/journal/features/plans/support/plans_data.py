from dataclasses import dataclass

from journal.features.plans.support.plan_status import PlanStatus
from journal.features.plans.support.started_plan import StartedPlan


@dataclass(frozen=True)
class PlansData:
    """The plans feature's reading: the approved plans, the started plan when one is, the status of every started plan, and the reports about a plan in review still unread."""

    approved: tuple[int, ...]
    started: StartedPlan | None
    started_plans: tuple[PlanStatus, ...] = ()
    review_reports: tuple[int, ...] = ()
