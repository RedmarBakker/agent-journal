from functools import partial

from journal.events.listener import Listener
from journal.events.rows.worker_queue_turn_ended import WorkerQueueTurnEnded
from journal.features.workers.support.worker_actions import WorkerActions
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue


class QueueTurnResumes(Listener[WorkerQueueTurnEnded]):
    """A worker whose process ended on a task it moved on to inside its queue is sent on in its own session with that task's brief, so a headless or Codex worker goes through its whole queue; the send runs on the deferred worker after the write that ended the turn, never inside another send, and only while nothing else has sent the worker a job since."""

    def __init__(self, actions: WorkerActions, tasks: Tasks, scope: Scope, deferred: ListenerQueue) -> None:
        self.actions, self.tasks, self.scope, self.deferred = actions, tasks, scope, deferred

    def handle(self, event: WorkerQueueTurnEnded) -> None:
        self.deferred.add(partial(self.resumed, event))

    def resumed(self, event: WorkerQueueTurnEnded) -> None:
        with self.scope.environment(event.environment_id):
            task = self.tasks.find(event.task)
            self.actions.queue_resumed(event.worker.id, f"Go on with your task {task.id}: {task.title}. {task.brief}\n\nProve each of its points, commit, and clock out when it is done.", Actor.system())
