from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.tasks import Tasks


def eligible_diagnostic(task: Task, tasks: Tasks) -> bool:
    return bool(task.state == TaskState.OPEN and not task.delegated and task.row_id not in tasks.unavailable_task_ids([task])
        and tasks.task_holder(task.row_id) is None and not tasks.has_worker_holder([task.row_id]))
