from datetime import datetime, timezone

from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.models.link import Link
from journal.models.plan_state import PlanState
from journal.repositories.plans import PLAN_LINK, Plans
from journal.support.time_source import TimeSource


class ReopenFinishedPlan(Listener[Created]):
    """A task put into a plan that is done, while the task is still to do, starts the plan again: a plan with open work is never shown done."""

    def __init__(self, plans: Plans, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.plans = plans

    def handle(self, event: Created) -> None:
        link = event.model
        if not isinstance(link, Link) or link.link_type != PLAN_LINK:
            return
        plan = self.plans.find(link.target.id)
        if plan.state == PlanState.FINISHED and not self.plans.finished(plan):
            self.plans.save(plan.unfinished("a task was added to it", self.time_source.moment().timestamp()), event.actor)
