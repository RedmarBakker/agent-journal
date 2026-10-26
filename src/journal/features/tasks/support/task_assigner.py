from journal.features.tasks.support.task_deliveries import TaskDeliveries
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.open_task import OpenTask
from journal.models.plan import Plan
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks


class TaskAssigner:
    """Which task an agent is handed next, the one place that decides it for every agent, in every work mode and at every moment, and the only one that reads auto mode for it: with auto mode off it hands nothing outside a started plan, no open, paused or blocked task, and a started plan goes task after task until its next checkpoint; with it on a plan is followed to its end. With it on, after a close it hands the task the plan it moves took in hand at the close or that plan's next open task, else, in the order the work mode delivers them, a started plan's next paused, blocked or open task, else the first paused, blocked or free open task outside it, never one a worker holds, and nothing when the plan keeps an older task in hand or the closer has another task in hand; at a stop or a quiet spell the work mode's first offer."""

    def __init__(self, tasks: Tasks, plans: Plans, deliveries: TaskDeliveries, settings: SettingRows) -> None:
        self.tasks, self.plans, self.deliveries, self.settings = tasks, plans, deliveries, settings

    def is_handing(self) -> bool:
        return bool(self.settings.option(TasksOptions.AUTO))

    def offered(self) -> OpenTask | None:
        free = self.deliveries.current().offers() if self.is_handing() else []
        return OpenTask(free[0].row_id, free[0].title, free[0].brief, 0) if free else None

    def paused_tasks(self) -> list[Task]:
        return self.tasks.paused_tasks() if self.is_handing() else []

    def blocked_tasks(self) -> list[Task]:
        return self.tasks.blocked_tasks() if self.is_handing() else []

    def unwaited_blocked_tasks(self) -> list[Task]:
        return self.tasks.blocked_without_wait() if self.is_handing() else []

    def open_ids(self, count: int) -> tuple[int, ...]:
        return tuple(self.tasks.open_page_ids(count)) if self.is_handing() else ()

    def plan_following(self, plan: Plan) -> Task | None:
        if not self.is_handing() and self.plans.checkpoint_plans(plan) is not None:
            return None
        return self.plans.following_task(plan)

    def next_task(self, closed: Task) -> OpenTask | None:
        return self.following(closed) if self.is_handing() else self.plan_successor(closed)

    def plan_successor(self, closed: Task) -> OpenTask | None:
        for plan in self.plans.started_plans(closed):
            current = self.plans.started_task(plan)
            if current is not None:
                return OpenTask(current.row_id, current.title, current.brief, plan.row_id)
        return None

    def following(self, closed: Task) -> OpenTask | None:
        started_plans = self.plans.started_plans(closed)
        ordered = self.deliveries.current().ordered_plans(self.plans.running_plans(), started_plans[0].row_id if started_plans else 0)
        if started_plans:
            return self.plan_next(ordered[0], closed) if ordered else self.loose_next()
        holder = self.tasks.holder(closed)
        if holder is not None and self.tasks.holder_task(holder) is not None:
            return None
        return self.plan_next(ordered[0], closed) if ordered else self.loose_next()

    def plan_next(self, plan: Plan, closed: Task) -> OpenTask | None:
        current = self.plans.started_task(plan)
        if current is not None and current.started_at is not None and closed.completed_at is not None and current.started_at < closed.completed_at:
            return None
        if current is not None:
            return OpenTask(current.row_id, current.title, current.brief, plan.row_id)
        for state in (TaskState.PAUSED, TaskState.BLOCKED):
            task = self.plans.first_task(plan, state, self.tasks.query())
            if task is not None:
                return OpenTask(task.row_id, task.title, task.brief, plan.row_id, state.value)
        task = self.plans.next_task(plan)
        return OpenTask(task.row_id, task.title, task.brief, plan.row_id) if task else self.loose_next()

    def loose_next(self) -> OpenTask | None:
        for state, tasks in ((TaskState.PAUSED, self.tasks.paused_tasks()), (TaskState.BLOCKED, self.tasks.blocked_tasks()), (TaskState.OPEN, self.plans.free())):
            if tasks:
                return OpenTask(tasks[0].row_id, tasks[0].title, tasks[0].brief, 0, state.value)
        return None
