from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor


class WorkerTaskAssigner:
    """The one place that chooses a worker's next task: the first of its queue, whether the queue was given task by task or as a whole plan or phase; handed over at its clock-out while its report is not due, or sent after a merge."""

    def __init__(self, tasks: Tasks) -> None:
        self.tasks = tasks

    def following(self, worker: Worker) -> Task | None:
        queue = self.tasks.queue(Ref.build(worker))
        return queue[0] if queue else None

    def handed(self, worker: Worker, task: Task, actor: Actor) -> Task:
        self.tasks.handover(task, Ref.build(worker), actor)
        return task
