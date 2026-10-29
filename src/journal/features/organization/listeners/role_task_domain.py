from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.organization.support.organization import Organization
from journal.models.link import Link
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.domain_rows import DomainRows
from journal.repositories.tasks import CURRENT_TASK_LINK, QUEUED_LINK, Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor

HANDED = (CURRENT_TASK_LINK, QUEUED_LINK)


class RoleTaskDomain(Listener[Created]):
    """A task handed or queued to a worker dispatched to a Role is tied to that Role's domain, read from the version of the folder the worker began on."""

    def __init__(self, organization: Organization, domains: DomainRows, workers: Workers, tasks: Tasks) -> None:
        self.organization, self.domains, self.workers, self.tasks = organization, domains, workers, tasks

    def handle(self, event: Created) -> None:
        if isinstance(event.model, Link) and event.model.link_type in HANDED and event.model.source.type == Worker.table() and event.model.target.type == Task.table():
            self.handed(event.model, event.actor)

    def handed(self, link: Link, actor: Actor) -> None:
        worker = self.workers.find(link.source.id)
        role = self.organization.at(worker.contract).role(worker.role) if worker.role else None
        if role is not None:
            self.domains.task_tied(self.tasks.find(link.target.id), role.domain, actor)
