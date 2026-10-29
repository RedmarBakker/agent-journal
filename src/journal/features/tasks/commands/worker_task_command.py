from journal.features.tasks.commands.task_command import TaskCommand
from journal.models.task import Task
from journal.support.caller import Caller


class WorkerTaskCommand(TaskCommand):
    """journal task as a worker runs it: it reads only the tasks it holds."""

    def readable(self, n: int, caller: Caller) -> Task:
        return self.tasks.worker_task(n, caller.worker_number)
