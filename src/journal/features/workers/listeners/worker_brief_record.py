from journal.events.listener import Listener
from journal.events.rows.worker_dispatched import WorkerDispatched
from journal.features.workers.support.worker_chat import WorkerChat
from journal.repositories.workers import Workers
from journal.support.voice_key import VoiceKey


class WorkerBriefRecord(Listener[WorkerDispatched]):
    """The job a worker is given, at its dispatch and at each send, is the first message of that job in its chat, from the agent that sent it."""

    def __init__(self, chat: WorkerChat, workers: Workers) -> None:
        self.chat, self.workers = chat, workers

    def handle(self, event: WorkerDispatched) -> None:
        worker = self.workers.find(event.worker.id)
        if worker.conversation():
            self.chat.briefed(worker, VoiceKey.create("brief", event.worker.ref(), f"{event.time}\n{event.brief}"))
