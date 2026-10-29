from journal.events.listener import Listener
from journal.events.models.deleted import Deleted
from journal.events.models.model_event import ModelEvent
from journal.events.models.saved import Saved
from journal.features.organization.support.domain_figures import DomainFigures
from journal.features.organization.support.organization import Organization
from journal.models.domain_row import DomainRow
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.domain_rows import DOMAIN_LINK, DomainRows
from journal.repositories.tasks import PLAN_LINK, QUEUED_LINK, CURRENT_TASK_LINK

COUNTED_LINKS = (QUEUED_LINK, CURRENT_TASK_LINK, PLAN_LINK, DOMAIN_LINK)


class DomainCountRecord(Listener[ModelEvent]):
    """A worker, task, plan or the link that hands a task on, once saved or, for a link, once removed, brings the figures of the domains it touches up to date in their rows: a task handed to another domain's Role refreshes the domain it left as well as the one it joined, and a queue that shrinks is counted again."""

    def __init__(self, figures: DomainFigures, organization: Organization, domains: DomainRows) -> None:
        self.figures, self.organization, self.domains = figures, organization, domains

    def handle(self, event: ModelEvent) -> None:
        if isinstance(event, (Saved, Deleted)):
            for name in dict.fromkeys(self.touched(event.model, isinstance(event, Deleted))):
                self.figures.refresh(name, event.actor)

    def touched(self, model, removed: bool) -> list[str]:
        if isinstance(model, Link) and model.link_type in COUNTED_LINKS:
            return [name for ref in (model.source, model.target) for name in self.named(ref)]
        if removed:
            return []
        if isinstance(model, Worker):
            return [self.domain_of(model)]
        if isinstance(model, Task):
            return self.domains.domain_names(model)
        if isinstance(model, Plan):
            return self.domains.board_names(model)
        return []

    def named(self, ref: Ref) -> list[str]:
        if ref.type == DomainRow.table():
            return [row.name for row in self.domains.numbered([ref.id])]
        if ref.type == Task.table():
            return [name for task in self.domains.tasks.numbered([ref.id]) for name in self.domains.domain_names(task)]
        if ref.type == Worker.table():
            return [self.domain_of(worker) for worker in self.domains.workers.numbered([ref.id])]
        return []

    def domain_of(self, worker: Worker) -> str:
        role = self.organization.at(worker.contract).role(worker.role) if worker.role else None
        return role.domain if role else ""
