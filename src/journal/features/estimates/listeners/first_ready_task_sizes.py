from journal.events.listener import Listener
from journal.events.rows.plan_readied import PlanReadied
from journal.repositories.task_sizes import TaskSizes


class FirstReadyTaskSizes(Listener[PlanReadied]):
    """Records the task sizes from the first time each plan is marked ready."""

    def __init__(self, sizes: TaskSizes) -> None:
        self.sizes = sizes

    def handle(self, event: PlanReadied) -> None:
        self.sizes.first_ready(event.plan_id, event.actor)
