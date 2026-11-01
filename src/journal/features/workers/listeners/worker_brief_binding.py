from journal.events.listener import Listener
from journal.events.rows.worker_session_bound import WorkerSessionBound
from journal.features.organization.support.seat_runner import SeatRunner
from journal.features.workers.support.worker_chat import WorkerChat
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers


class WorkerBriefBinding(Listener[WorkerSessionBound]):
    """A non-seat worker's brief becomes the first message of its chat when its session binds."""

    def __init__(self, workers: Workers, chat: WorkerChat, seats: SeatRunner, scope: Scope) -> None:
        self.workers, self.chat, self.seats, self.scope = workers, chat, seats, scope

    def handle(self, event: WorkerSessionBound) -> None:
        with self.scope.environment(event.environment_id):
            worker = self.workers.find(event.row_id)
            if not self.seats.applies(worker):
                self.chat.briefed_once(worker)
