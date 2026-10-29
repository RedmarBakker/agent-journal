from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.organization.support.role_queue import RoleQueue
from journal.models.link import Link
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.tasks import QUEUED_LINK
from journal.repositories.workers import Workers


class RoleQueueFeeder(Listener[Created]):
    """Order a shared Role's queued tasks when the journal adds one."""

    def __init__(self, queue: RoleQueue, workers: Workers) -> None:
        self.queue, self.workers = queue, workers

    def handle(self, event: Created) -> None:
        model = event.model
        if isinstance(model, Link) and model.link_type == QUEUED_LINK and model.source.type == Worker.table() and model.target.type == Task.table():
            self.queue.feed(self.workers.find(model.source.id), event.actor)
