from itertools import zip_longest

from journal.features.tasks.support.task_delivery import TaskDelivery
from journal.models.plan import Plan
from journal.models.task import Task


class RoundRobinDelivery(TaskDelivery):
    """Delivery of the orchestrator: the next task of every started plan goes out in turn, the plan after the one a task closed in first, and the plans with nothing to hand out are left out."""

    def ordered_plans(self, started: list[Plan], closed_plan_id: int) -> list[Plan]:
        ready = [plan for plan in started if self.plans.started_task(plan) or self.plans.following_task(plan)]
        return [*(plan for plan in ready if plan.row_id > closed_plan_id), *(plan for plan in ready if plan.row_id <= closed_plan_id)]

    def planned_offers(self, started: list[Plan]) -> list[Task]:
        queues = [self.plans.queued_tasks(plan) for plan in started]
        return [task for group in zip_longest(*queues) for task in group if task is not None]
