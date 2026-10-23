import time
from typing import Callable

from journal.features.workers.support.pool_worker_moves import DELIVERED, ENDED, READY
from journal.features.workers.support.worker_end import WorkerEnd
from journal.features.workers.support.worker_reports import WorkerReports
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.worker import Worker
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.host_writer import HostWriter
from sync_server.host_request import HostRequest


class PoolWorkerWrites(HostWriter):
    """The moves of a pool worker running on a teammate's machine, made here, on the journal that dispatched it, so its dispatcher hears them: clocked in, clocked out with its report, and its run's end."""

    def __init__(self, workers: Workers, reports: WorkerReports, runner: WorkerRunner, environments: Environments, scope: Scope) -> None:
        self.workers, self.reports, self.runner, self.environments, self.scope = workers, reports, runner, environments, scope

    def makers(self) -> dict[str, Callable[[HostRequest], None]]:
        return {READY: self.ready, DELIVERED: self.delivered, ENDED: self.ended}

    def ready(self, request: HostRequest) -> None:
        self.scoped(request, lambda worker, actor: self.workers.save(worker.ready(time.time()), actor))

    def delivered(self, request: HostRequest) -> None:
        self.scoped(request, lambda worker, actor: self.delivery(worker, request.body["report"], actor))

    def delivery(self, worker: Worker, report: str, actor: Actor) -> None:
        self.reports.posted(worker, report, actor)
        self.workers.save(self.workers.find(worker.row_id).delivered(time.time()), actor)

    def ended(self, request: HostRequest) -> None:
        end = WorkerEnd.parsed(request.body)
        self.scoped(request, lambda worker, actor: self.end(worker.with_(resume=end.resume or worker.resume), end, actor))

    def end(self, worker: Worker, end: WorkerEnd, actor: Actor) -> None:
        if not self.runner.awaits_report(worker):
            self.runner.close(worker, end.outcome, actor)
            return
        self.runner.reported(worker.with_(touched_paths=end.touched), end.outcome, end.summary, actor)

    def scoped(self, request: HostRequest, change: Callable[[Worker, Actor], None]) -> None:
        worker_id = request.body["worker_id"]
        for environment in self.environments.keyed(request.environment_key):
            with self.scope.environment(environment.row_id):
                change(self.workers.find(worker_id), Actor.worker(worker_id))
