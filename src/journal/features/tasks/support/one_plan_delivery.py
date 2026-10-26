from journal.features.tasks.support.task_delivery import TaskDelivery
from journal.models.plan import Plan
from journal.models.task import Task


class OnePlanDelivery(TaskDelivery):
    """Delivery of the builder and the solo agent: tasks come from one plan only, the started one that a task just closed in or else the oldest, and it is finished before another plan's task goes out."""

    def ordered_plans(self, started: list[Plan], closed_plan_id: int) -> list[Plan]:
        return [plan for plan in started if plan.row_id == closed_plan_id] or started[:1]

    def planned_offers(self, started: list[Plan]) -> list[Task]:
        task = self.plans.next_task(started[0]) if started else None
        return [task] if task is not None else []
