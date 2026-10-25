from journal.events.listener import Listener
from journal.events.rows.worker_queue_turn_ended import WorkerQueueTurnEnded
from journal.features.workers.support.worker_actions import WorkerActions
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor


class QueueTurnResumes(Listener[WorkerQueueTurnEnded]):
    """A worker whose process ended on a task it moved on to inside its queue is sent on in its own session with that task's brief, so a headless or Codex worker goes through its whole queue."""

    def __init__(self, actions: WorkerActions, tasks: Tasks, scope: Scope) -> None:
        self.actions, self.tasks, self.scope = actions, tasks, scope

    def handle(self, event: WorkerQueueTurnEnded) -> None:
        with self.scope.environment(event.environment_id):
            task = self.tasks.find(event.task)
            self.actions.send(event.worker.id, f"Go on with your task {task.id}: {task.title}. {task.brief}\n\nProve each of its points, commit, and clock out when it is done.", None, Actor.system())
