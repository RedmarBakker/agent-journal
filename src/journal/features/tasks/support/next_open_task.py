from journal.models.open_task import OpenTask
from journal.models.plan import Plan
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks


class NextOpenTask:
    """What a task's close leaves open next, closed by command or by a commit: the task the plan it moves took in hand at the close or that plan's next open task, else a started plan's next paused, blocked or open task, else the first paused, blocked or free open task outside it, never one a worker holds; nothing when the plan keeps an older task in hand or the closer has another task in hand."""

    def __init__(self, tasks: Tasks, plans: Plans) -> None:
        self.tasks, self.plans = tasks, plans

    def following(self, closed: Task) -> OpenTask | None:
        started_plans = self.plans.started_plans(closed)
        if started_plans:
            return self.plan_next(started_plans[0], closed)
        holder = self.tasks.holder(closed)
        if holder is not None and self.tasks.holder_task(holder) is not None:
            return None
        active_plans = self.plans.running_plans()
        if active_plans:
            return self.plan_next(active_plans[0], closed)
        return self.loose_next()

    def plan_next(self, plan: Plan, closed: Task) -> OpenTask | None:
        current = self.plans.started_task(plan)
        if current is not None and current.started_at is not None and closed.finished_at is not None and current.started_at < closed.finished_at:
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
