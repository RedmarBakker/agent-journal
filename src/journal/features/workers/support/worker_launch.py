import time

from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.worker import Worker
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class WorkerLaunch:
    """The one way an agent is sent: record its dispatch before starting its process or seat session, which writes its chat mark."""

    def __init__(self, workers: Workers, runner: WorkerRunner, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.workers, self.runner = workers, runner

    def launched(self, worker: Worker, actor: Actor, repositories: tuple[str, ...] = (), branch: str = "") -> Worker:
        placed = self.workers.save(worker.with_(repositories=repositories or worker.repositories, branch=branch or worker.branch).dispatched(self.time_source.seconds()), actor)
        self.runner.start(placed, actor)
        return self.workers.find(worker.row_id)
