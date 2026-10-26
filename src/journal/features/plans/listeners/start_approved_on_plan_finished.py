from journal.events.listener import Listener
from journal.events.rows.plan_finished import PlanFinished
from journal.features.plans.support.approved_plan_start import ApprovedPlanStart


class StartApprovedOnPlanFinished(Listener[PlanFinished]):
    """At a plan finishing with no plan started, the oldest approved plan starts by itself."""

    def __init__(self, start: ApprovedPlanStart) -> None:
        self.start = start

    def handle(self, event: PlanFinished) -> None:
        self.start.run()
