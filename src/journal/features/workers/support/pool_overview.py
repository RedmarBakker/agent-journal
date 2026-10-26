import time

from journal.features.workers.support.pool_worker_moves import PoolWorkerMoves
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.pool_worker_line import PoolWorkerLine
from journal.models.pool_job_state import PoolJobState
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.repositories.pool_jobs import PoolJobs
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.features.workers.workers_options import WorkersOptions
from journal.support.time_source import TimeSource

STOP_REASON = "stopped from the Team page by the member whose machine runs it"


class PoolOverview:
    """The worker pool as the Team page shows it: the slots this machine gives and how many are free, the minutes of pool work it ran today against its daily cap, the pool workers it runs for teammates, this journal's pool workers running on other machines, and every pool worker the team runs; and the stop of one it runs, from that page."""

    def __init__(self, jobs: PoolJobs, workers: Workers, tasks: Tasks, environments: Environments, scope: Scope, settings: SettingRows, owners: EnvironmentOwners, moves: PoolWorkerMoves, actions: WorkerActions, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.jobs, self.workers, self.tasks, self.environments, self.scope, self.settings = jobs, workers, tasks, environments, scope, settings
        self.owners, self.moves, self.actions = owners, moves, actions

    def slots(self) -> int:
        return self.settings.integer(WorkersOptions.POOL_SLOTS)

    def minute_cap(self) -> int:
        return self.settings.integer(WorkersOptions.POOL_MINUTES)

    def minutes_today(self) -> int:
        return round(self.jobs.today_minutes(self.time_source.seconds()))

    def lent(self) -> list[PoolWorkerLine]:
        return [line for job in self.jobs.all_matching(state=PoolJobState.STARTED) for line in self.job_lines(job.environment_key, job.worker_id, self.owners.person_name(job.account_id))]

    def job_lines(self, key: str, worker_id: int, owner: str) -> list[PoolWorkerLine]:
        lines = []
        for environment in self.environments.keyed(key):
            with self.scope.environment(environment.row_id):
                lines += [self.line(worker, owner) for worker in self.workers.all_matching(id=worker_id)]
        return lines

    def remote_runs(self) -> list[PoolWorkerLine]:
        return [self.line(worker, f"machine {worker.device}") for worker in self.pool_workers() if self.moves.is_remote_run(worker)]

    def team(self) -> list[PoolWorkerLine]:
        return [self.line(worker, f"machine {worker.device}" if worker.device else "waiting for a machine") for worker in self.pool_workers()]

    def pool_workers(self) -> list[Worker]:
        workers = []
        for environment in self.environments.working():
            with self.scope.environment(environment.row_id):
                workers += self.workers.running_pool_workers()
        return workers

    def line(self, worker: Worker, owner: str) -> PoolWorkerLine:
        task_ids = self.tasks.holder_task_ids(Ref.build(worker))
        minutes = round((self.time_source.seconds() - worker.began) / 60) if worker.began else 0
        return PoolWorkerLine(worker.pool_request, worker.id, worker.name, self.tasks.find(task_ids[0]).title if task_ids else "", owner, minutes)

    def stop(self, request: int, actor: Actor) -> None:
        for job in self.jobs.all_matching(request_id=request, state=PoolJobState.STARTED):
            for environment in self.environments.keyed(job.environment_key):
                with self.scope.environment(environment.row_id):
                    self.actions.stop(job.worker_id, STOP_REASON, actor)
