from journal.events.listener import Listener
from journal.events.rows.worker_ready import WorkerReady
from journal.features.workers.support.worker_assigner import WorkerAssigner
from journal.repositories.workers import Workers


class WorkerAssignment(Listener[WorkerReady]):
    """A worker that clocks in on the task it holds is put to work on it."""

    def __init__(self, workers: Workers, assigner: WorkerAssigner) -> None:
        self.workers, self.assigner = workers, assigner

    def handle(self, event: WorkerReady) -> None:
        self.assigner.assigned(self.workers.find(event.worker.id))
