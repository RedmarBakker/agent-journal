from journal.events.listener import Listener
from journal.events.models.saving import Saving
from journal.models.link import Link
from journal.repositories.tasks import Tasks


class TaskCycleCheck(Listener[Saving]):
    """A planned prerequisite, delivery gate or runtime wait that closes a task cycle is refused."""

    def __init__(self, tasks: Tasks) -> None:
        self.tasks = tasks

    def handle(self, event: Saving) -> None:
        link = event.model
        if isinstance(link, Link):
            self.tasks.require_acyclic_link(link)
