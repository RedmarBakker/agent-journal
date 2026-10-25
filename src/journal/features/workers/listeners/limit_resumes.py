from journal.events.clock_ticked import ClockTicked
from journal.events.listener import Listener
from journal.features.workers.support.worker_actions import WorkerActions
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor

RESUME_JOB = "The usage limit has reset: go on with your task where you stopped, and clock out when it is done."


class LimitResumes(Listener[ClockTicked]):
    """Every tick, each worker that stopped at the provider's usage limit and whose reset time has come is sent on in its own session, with its memory and its task as they were."""

    def __init__(self, workers: Workers, actions: WorkerActions, scope: Scope) -> None:
        self.workers, self.actions, self.scope = workers, actions, scope

    def handle(self, event: ClockTicked) -> None:
        for worker in self.workers.limit_passed(event.time):
            with self.scope.environment(worker.environment_id):
                self.actions.send(worker.row_id, RESUME_JOB, None, Actor.system())
