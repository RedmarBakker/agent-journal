from journal.events.listener import Listener
from journal.events.rows.worker_agent_created import WorkerAgentCreated
from journal.features.workers.support.worker_assigner import WorkerAssigner
from journal.features.workers.support.worker_chat import WorkerChat
from journal.repositories.workers import Workers


class WorkerSessionAssignment(Listener[WorkerAgentCreated]):
    """A worker that clocked in before its session had an agent row is put to work as soon as the row is made, and its job, which had no session to be written to, becomes the first message of its chat."""

    def __init__(self, workers: Workers, assigner: WorkerAssigner, chat: WorkerChat) -> None:
        self.workers, self.assigner, self.chat = workers, assigner, chat

    def handle(self, event: WorkerAgentCreated) -> None:
        for row in self.workers.session_worker(event.agent_session):
            self.chat.briefed_once(row)
            self.assigner.assigned(row)
