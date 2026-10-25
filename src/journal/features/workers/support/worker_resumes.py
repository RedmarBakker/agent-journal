from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.worker import Worker
from journal.providers.providers import Providers


class WorkerResumes:
    """Whether a worker can go on in its last session: it left one, and the conversation of it is still there."""

    def __init__(self, providers: Providers, branch: WorkerBranch) -> None:
        self.providers, self.branch = providers, branch

    def is_resumable(self, worker: Worker) -> bool:
        return bool(worker.resume) and self.providers.lookup(worker.provider).transcript(self.branch.place(worker), worker.resume) is not None
