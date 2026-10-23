from journal.models.pool_job_state import PoolJobState
from journal.models.worker import Worker
from journal.repositories.pool_jobs import PoolJobs
from journal.sync.team_server_link import TeamServerLink
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.sync.hosts import Hosts

READY = "worker_ready"
DELIVERED = "worker_delivered"
ENDED = "worker_ended"
UNCLAIMED = "pool_unclaimed"
STOPPED = "worker_stopped"
OFFLINE_MACHINE = "pool_machine_offline"


class PoolWorkerMoves:
    """On a machine running a pool worker for another journal: whether a worker's moves belong to another journal, the host of its environment, the request that asks that journal to make one, so its events fire where its dispatcher waits, and the end of its pool job here, which frees the slot and tells the team server the request is done."""

    def __init__(self, hosts: Hosts, environments: Environments, jobs: PoolJobs, link: TeamServerLink) -> None:
        self.hosts, self.environments, self.jobs, self.link = hosts, environments, jobs, link

    def is_remote(self, worker: Worker) -> bool:
        return bool(worker.pool_request) and not self.hosts.is_host(self.environments.find(worker.environment_id))

    def ended(self, worker: Worker) -> None:
        for job in self.jobs.all_matching(worker_id=worker.id, state=PoolJobState.STARTED):
            self.jobs.save(job.finished(), Actor.system())
            self.link.finish_host_request(job.request_id)

    def ask(self, worker: Worker, kind: str, body: dict, actor: Actor) -> None:
        self.hosts.ask(self.environments.find(worker.environment_id), kind, {"worker_id": worker.id, **body}, actor)
