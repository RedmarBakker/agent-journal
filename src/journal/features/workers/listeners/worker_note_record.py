from journal.events.listener import Listener
from journal.events.rows.worker_notified import WorkerNotified
from journal.features.workers.support.worker_chat import WorkerChat
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class WorkerNoteRecord(Listener[WorkerNotified]):
    """A note given to a running worker is a message in its chat, written once where it is sent, never again from its transcript, and a message sent to it in the chat of the agent that dispatched it, as a message to any other agent is."""

    def __init__(self, chat: WorkerChat, workers: Workers) -> None:
        self.chat, self.workers = chat, workers

    def handle(self, event: WorkerNotified) -> None:
        actor = Actor.parse(event.sender)
        self.chat.instruction(self.workers.find(event.worker.id), event.text, actor)
        self.chat.sent(event.worker, event.text, actor)
