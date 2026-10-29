from journal.engine.job import Job
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.worker import Worker
from journal.support.actor import Actor
from journal.repositories.scope import Scope


class WorkerWatch(Job):
    """Every two seconds, each worker the journal found still out at boot is checked: one whose process has ended has its report filed from its files, one past its time limit is stopped, so a restart never loses a worker."""

    interval_seconds = 2.0

    def __init__(self, runner: WorkerRunner, scope: Scope) -> None:
        self.runner, self.scope = runner, scope
        self.watched: list[Worker] = []

    def add(self, worker: Worker) -> None:
        self.watched.append(worker)

    def tick(self, time: float) -> None:
        known = {worker.id for worker in self.watched}
        self.watched.extend(worker for worker in self.runner.seat_workers() if worker.id not in known)
        for worker in list(self.watched):
            with self.scope.environment(worker.environment_id):
                current = self.runner.workers.find(worker.row_id)
                if self.runner.seats.applies(current) and current.is_running():
                    self.runner.recover_seat(current, Actor.system())
                if self.runner.is_finished(current, Actor.system()):
                    self.watched.remove(worker)
