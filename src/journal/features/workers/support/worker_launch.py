import time

from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.worker import Worker
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class WorkerLaunch:
    """The one way an agent is sent, a worker an agent dispatches and a verifier the journal sends alike: its process started and its row marked dispatched, which writes its chat mark."""

    def __init__(self, workers: Workers, runner: WorkerRunner) -> None:
        self.workers, self.runner = workers, runner

    def launched(self, worker: Worker, actor: Actor, repositories: tuple[str, ...] = (), branch: str = "") -> Worker:
        self.runner.start(worker, actor)
        started = self.workers.find(worker.row_id)
        return self.workers.save(started.with_(repositories=repositories or started.repositories, branch=branch or started.branch).dispatched(time.time()), actor)
