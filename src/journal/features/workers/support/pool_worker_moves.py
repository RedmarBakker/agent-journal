from journal.models.worker import Worker
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.sync.hosts import Hosts

READY = "worker_ready"
DELIVERED = "worker_delivered"
ENDED = "worker_ended"


class PoolWorkerMoves:
    """On a machine running a pool worker for another journal: whether a worker's moves belong to another journal, the host of its environment, and the request that asks that journal to make one, so its events fire where its dispatcher waits."""

    def __init__(self, hosts: Hosts, environments: Environments) -> None:
        self.hosts, self.environments = hosts, environments

    def is_remote(self, worker: Worker) -> bool:
        return bool(worker.pool_request) and not self.hosts.is_host(self.environments.find(worker.environment_id))

    def ask(self, worker: Worker, kind: str, body: dict, actor: Actor) -> None:
        self.hosts.ask(self.environments.find(worker.environment_id), kind, {"worker_id": worker.id, **body}, actor)
