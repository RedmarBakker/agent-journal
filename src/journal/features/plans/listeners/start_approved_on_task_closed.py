from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.plans.support.approved_plan_start import ApprovedPlanStart


class StartApprovedOnTaskClosed(Listener[TaskClosed]):
    """At a task closing with no plan started, the oldest approved plan starts by itself."""

    def __init__(self, start: ApprovedPlanStart) -> None:
        self.start = start

    def handle(self, event: TaskClosed) -> None:
        self.start.run()
