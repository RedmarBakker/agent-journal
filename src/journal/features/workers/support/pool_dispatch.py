from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.environments import Environments
from journal.support.rejection import Rejection
from journal.sync.host_desk import HostDesk
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink
from journal.version import VERSION
from sync_server.pool_ask_request import PoolAskRequest


class PoolDispatch:
    """Sends a worker to the team's pool: pushes the head of its environment's checkout to origin as the base its worktree is cut from on the machine that takes it, and asks the pool with the worker's name, task, profile, provider, brief, base and library folders, answering the team server's number of the request."""

    def __init__(self, branch: WorkerBranch, link: TeamServerLink, account: TeamAccount, environments: Environments) -> None:
        self.branch, self.link, self.account, self.environments = branch, link, account, environments

    def send(self, worker: Worker, task: Task) -> int:
        base = self.branch.pool_base(worker)
        pushed = self.branch.git("push", "origin", f"HEAD:refs/heads/{base}", cwd=self.branch.checkout(worker))
        if pushed.returncode != 0:
            raise Rejection(f"worker {worker.name} was not sent to the pool: its base could not be pushed to origin: {pushed.stderr.strip()}")
        body = {"worker_id": worker.id, "worker": worker.name, "task": task.id, "title": task.title, "profile": worker.profile, "provider": worker.provider, "brief": worker.brief, "base": base, "libraries": list(worker.library_links), "copies": list(worker.library_copies)}
        environment = self.environments.find(worker.environment_id)
        return self.link.ask_pool(PoolAskRequest(environment.key, HostDesk.POOL_WORKER, body, self.account.user_number(), VERSION))
