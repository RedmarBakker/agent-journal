from journal.events.listener import Listener
from journal.events.models.synced_update import SyncedUpdate
from journal.models.task import Task
from journal.repositories.tasks import Tasks


class PulledTaskMoves(Listener[SyncedUpdate]):
    """A task's change pulled from the team is heard by the agent of each environment on this machine that drives it, as the same change made here would be, and by no other."""

    def __init__(self, tasks: Tasks) -> None:
        self.tasks = tasks

    def handle(self, event: SyncedUpdate) -> None:
        if isinstance(event.model, Task):
            self.tasks.pulled_dispatched(event.model, event.previous, event.actor)
