from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.pool_job_state import PoolJobState
from journal.models.worker import Worker
from journal.repositories.pool_jobs import PoolJobs
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink
from sync_server.device_ask_request import DeviceAskRequest
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.sync.hosts import Hosts

READY = "worker_ready"
DELIVERED = "worker_delivered"
ENDED = "worker_ended"
UNCLAIMED = "pool_unclaimed"
STOPPED = "worker_stopped"
OFFLINE_MACHINE = "pool_machine_offline"
REDO = "worker_redo"
NOTE = "worker_note"
CLEANUP = "worker_cleanup"


class PoolWorkerMoves:
    """On a machine running a pool worker for another journal: whether a worker's moves belong to another journal, the host of its environment, the request that asks that journal to make one, so its events fire where its dispatcher waits, on the dispatching journal the request that asks the machine running it to make a send-back or a word, the clearing of a pool worker that is done with, its branches on origin deleted and its machine told to drop its worktree, and the end of its pool job here, which frees the slot and tells the team server the request is done."""

    def __init__(self, hosts: Hosts, environments: Environments, jobs: PoolJobs, link: TeamServerLink, account: TeamAccount, branch: WorkerBranch) -> None:
        self.hosts, self.environments, self.jobs, self.link, self.account, self.branch = hosts, environments, jobs, link, account, branch

    def is_remote(self, worker: Worker) -> bool:
        return bool(worker.pool_request) and not self.hosts.is_host(self.environments.find(worker.environment_id))

    def is_local_dispatch(self, worker: Worker) -> bool:
        return bool(worker.pool_request) and not self.is_remote(worker)

    def is_remote_run(self, worker: Worker) -> bool:
        return self.is_local_dispatch(worker) and bool(worker.device) and not worker.is_device(self.account.device())

    def ask_runner(self, worker: Worker, kind: str, body: dict) -> None:
        environment = self.environments.find(worker.environment_id)
        self.link.ask_device(DeviceAskRequest(int(worker.device), environment.key, kind, {"worker_id": worker.id, **body}, self.account.user_number()))

    def cleared(self, worker: Worker) -> None:
        if not self.is_local_dispatch(worker):
            return
        self.branch.clear_pool(worker)
        if self.is_remote_run(worker):
            self.ask_runner(worker, CLEANUP, {})

    def ended(self, worker: Worker) -> None:
        for job in self.jobs.all_matching(worker_id=worker.id, state=PoolJobState.STARTED):
            self.jobs.save(job.finished(), Actor.system())
            self.link.finish_host_request(job.request_id)

    def ask(self, worker: Worker, kind: str, body: dict, actor: Actor) -> None:
        self.hosts.ask(self.environments.find(worker.environment_id), kind, {"worker_id": worker.id, **body}, actor)
