from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.support.rejection import Rejection


class WorkerResumes:
    """Whether a worker can go on in its last session: it left one, and the conversation of it is still there; a worker with no place to start from is not resumable."""

    def __init__(self, providers: Providers, branch: WorkerBranch) -> None:
        self.providers, self.branch = providers, branch

    def is_resumable(self, worker: Worker) -> bool:
        if not worker.resume:
            return False
        try:
            place = self.branch.place(worker)
        except Rejection:
            return False
        return self.providers.lookup(worker.provider).transcript(place, worker.resume) is not None
