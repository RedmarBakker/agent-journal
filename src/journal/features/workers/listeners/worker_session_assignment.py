from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.workers.support.worker_assigner import WorkerAssigner
from journal.models.agent import Agent
from journal.models.agent_role import AgentRole
from journal.repositories.workers import Workers


class WorkerSessionAssignment(Listener[Created]):
    """A worker that clocked in before its session had an agent row is put to work as soon as the row is made."""

    def __init__(self, workers: Workers, assigner: WorkerAssigner) -> None:
        self.workers, self.assigner = workers, assigner

    def handle(self, event: Created) -> None:
        if isinstance(event.model, Agent) and event.model.role == AgentRole.WORKER and event.model.session:
            for row in self.workers.session_worker(event.model.session):
                self.assigner.assigned(row)
