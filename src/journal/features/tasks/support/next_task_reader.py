from journal.models.open_task import OpenTask
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks


class NextTaskReader:
    """The task the holder of a closed task has in hand now, which its task assigner started when the task closed, named with the plan it is in; none when it took up nothing."""

    def __init__(self, tasks: Tasks, plans: Plans) -> None:
        self.tasks, self.plans = tasks, plans

    def holder_task(self, closed: Task) -> OpenTask | None:
        holder = self.tasks.holder(closed)
        current = self.tasks.holder_task(holder) if holder is not None else None
        if current is None or current.row_id == closed.row_id or current.state != TaskState.STARTED:
            return None
        plan = next(iter(self.plans.started_plans(current)), None)
        return OpenTask(current.row_id, current.title, current.brief, plan.row_id if plan else 0, current.state.value)
