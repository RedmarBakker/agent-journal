from journal.engine.job import Job
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.workers_options import WorkersOptions
from journal.models.worker import Worker
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class WorktreeCleanup(Job):
    """Every hour, in every environment of this machine, deletes the worktree of each retired worker and retires each worker at rest past the set hours with nothing unmerged, worktree and all; a worktree holding uncommitted files stays."""

    interval_seconds = 3600.0

    def __init__(self, workers: Workers, branch: WorkerBranch, actions: WorkerActions, environments: Environments, scope: Scope, settings: SettingRows) -> None:
        self.workers, self.branch, self.actions, self.environments, self.scope, self.settings = workers, branch, actions, environments, scope, settings

    def tick(self, time: float) -> None:
        for environment in self.environments.working():
            with self.scope.environment(environment.row_id):
                for worker in self.workers.with_worktree():
                    self.cleaned(worker, time)

    def cleaned(self, worker: Worker, time: float) -> None:
        if not self.branch.folder(worker).is_dir():
            return
        if worker.adopted:
            self.branch.dropped(worker)
            return
        if self.is_retirement_due(worker, time):
            self.actions.complete(worker.id, f"at rest for over {self.settings.integer(WorkersOptions.IDLE_HOURS)} hours", Actor.system())

    def is_retirement_due(self, worker: Worker, time: float) -> bool:
        hours = self.settings.integer(WorkersOptions.IDLE_HOURS)
        return bool(hours) and worker.is_retirable(time, 3600 * hours) and not self.branch.unmerged_count(worker)
