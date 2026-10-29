from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.domain_row import DomainRow
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.repository import Repository
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

DOMAIN_LINK = "belongs_to_domain"


class DomainRows(Repository[DomainRow]):
    """The organization's domains that tasks were handed to, the same for every environment, and the link that ties a task to the domain of the Role it was handed to: one domain per task, the last Role's."""

    model = DomainRow

    def __init__(self, connection: Connection, bus: Bus, links: Links, tasks: Tasks, time_source: TimeSource) -> None:
        super().__init__(connection, bus, time_source)
        self.links, self.tasks = links, tasks

    def task_tied(self, task: Task, name: str, actor: Actor) -> Link:
        with self.writing():
            domain = Ref.build(self.named(name, actor))
            for link in self.links.all_matching(source=Ref.build(task), link_type=DOMAIN_LINK):
                if link.target != domain:
                    self.links.delete(link, actor)
            return self.links.linked(Ref.build(task), domain, DOMAIN_LINK, actor)

    def named(self, name: str, actor: Actor) -> DomainRow:
        with self.writing():
            rows = self.all_matching(name=name)
            return rows[0] if rows else self.save(DomainRow(name=name), actor)

    def domain_tasks(self, name: str) -> list[Task]:
        rows = self.all_matching(name=name)
        if not rows:
            return []
        tied = self.links.query().filter(link_type=DOMAIN_LINK, target=Ref.build(rows[0])).filter_ref("source", self.tasks.query())
        return self.tasks.selected_globally(self.tasks.query().filter_existing(tied).order("id"))
