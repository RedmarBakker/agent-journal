from journal.events.listener import Listener
from journal.events.pool_job_arrived import PoolJobArrived
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.pool_job import PoolJob
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.repositories.pool_jobs import PoolJobs
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.worktree_failure import WorktreeFailure
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink


class PoolJobIntake(Listener[PoolJobArrived]):
    """Takes up a worker the team's pool offered this machine, off the sync thread: turns it down while every slot this machine gives is taken, claims it so no other machine starts it, fetches its base, cuts its worktree from it, runs it on the model its profile names here and tells the team server it is taken up. A job whose worker row has not reached this machine yet is forgotten, so the next pull brings it again; one that cannot be cut is turned down with the reason, so the server offers it to another machine."""

    def __init__(self, jobs: PoolJobs, link: TeamServerLink, workers: Workers, runner: WorkerRunner, branch: WorkerBranch, settings: SettingRows, scope: Scope, environments: Environments, providers: Providers, profiles: ProfileFiles) -> None:
        self.jobs, self.link, self.workers, self.runner, self.branch, self.settings = jobs, link, workers, runner, branch, settings
        self.scope, self.environments, self.providers, self.profiles = scope, environments, providers, profiles

    def handle(self, event: PoolJobArrived) -> None:
        from journal.features.workers.feature import Workers as Feature
        job = self.jobs.job(event.request_id)
        if self.jobs.started_count() >= self.settings.integer(Feature.POOL_SLOTS):
            self.declined(job, "every worker slot this machine gives the pool is taken")
            return
        environments = self.environments.keyed(job.environment_key)
        with self.scope.environment(environments[0].row_id if environments else 0):
            if not environments or not self.workers.all_matching(id=job.worker_id):
                self.jobs.delete(job, Actor.system())
                return
            self.claimed(job, self.workers.find(job.worker_id))

    def claimed(self, job: PoolJob, worker: Worker) -> None:
        try:
            self.link.claim_request(job.request_id)
        except TeamRefusal as taken:
            self.jobs.save(job.declined(str(taken)), Actor.system())
            return
        fetched = self.branch.git("fetch", "origin", f"refs/heads/{worker.base}:refs/remotes/origin/{worker.base}", cwd=self.branch.checkout(worker))
        if fetched.returncode != 0:
            self.declined(job, f"its base {worker.base} could not be fetched from origin: {fetched.stderr.strip()}")
            return
        local = worker.with_(model=self.providers.lookup(worker.provider).profile_model(self.profiles.read(job.profile)))
        try:
            repositories = self.runner.workplace(local)
        except WorktreeFailure as failed:
            self.declined(job, str(failed))
            return
        self.runner.start(self.workers.save(local.with_(repositories=repositories), Actor.user(job.account_id)), Actor.user(job.account_id))
        self.jobs.save(job.started(), Actor.system())
        self.link.finish_host_request(job.request_id)

    def declined(self, job: PoolJob, reason: str) -> None:
        self.link.decline_request(job.request_id, reason)
        self.jobs.save(job.declined(reason), Actor.system())
