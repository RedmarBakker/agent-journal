from journal.events.listener import Listener
from journal.events.rows.worker_session_bound import WorkerSessionBound
from journal.features.workers.support.worker_chat import WorkerChat
from journal.repositories.workers import Workers


class WorkerBriefBinding(Listener[WorkerSessionBound]):
    """A worker's job, which had no session to be written to at its dispatch, becomes the first message of its chat when its session binds."""

    def __init__(self, workers: Workers, chat: WorkerChat) -> None:
        self.workers, self.chat = workers, chat

    def handle(self, event: WorkerSessionBound) -> None:
        self.chat.briefed_once(self.workers.find(event.row_id))
