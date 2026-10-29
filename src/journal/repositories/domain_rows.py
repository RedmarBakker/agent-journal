from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.models.board_phase import BoardPhase
from journal.models.check import Check
from journal.models.domain_row import DomainRow
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.question import Question
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.links import Links
from journal.repositories.repository import Repository
from journal.repositories.tasks import CURRENT_TASK_LINK, FINISHED_LINK, PLAN_LINK, Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

DOMAIN_LINK = "belongs_to_domain"
BOARD_LINKS = {phase: f"on_board_{phase.value}" for phase in BoardPhase}
REVIEWS = (Check.table(), Question.table())


class DomainRows(Repository[DomainRow]):
    """The organization's domains that tasks were handed to, the same for every environment; the link that ties a task to the domain of the Role it was handed to, one domain per task, the last Role's; and the link from a plan to each domain's board that names the phase it stands in there."""

    model = DomainRow

    def __init__(self, connection: Connection, bus: Bus, links: Links, tasks: Tasks, workers: Workers, time_source: TimeSource) -> None:
        super().__init__(connection, bus, time_source)
        self.links, self.tasks, self.workers = links, tasks, workers

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

    def domain_names(self, task: Task) -> list[str]:
        return [row.name for row in self.numbered(ref.id for ref in self.links.targets(task, DOMAIN_LINK))]

    def domain_tasks(self, name: str) -> list[Task]:
        rows = self.all_matching(name=name)
        return self.tasks.selected_globally(self.domain_task_query(rows[0]).order("id")) if rows else []

    def plan_domain_tasks(self, plan: Plan, name: str) -> list[Task]:
        rows = self.all_matching(name=name)
        planned = self.links.query().filter(link_type=PLAN_LINK, target=Ref.build(plan)).filter_ref("source", self.tasks.query())
        return self.tasks.selected_globally(self.domain_task_query(rows[0]).filter_existing(planned).order("id")) if rows else []

    def domain_task_query(self, row: DomainRow) -> Query:
        tied = self.links.query().filter(link_type=DOMAIN_LINK, target=Ref.build(row)).filter_ref("source", self.tasks.query())
        return self.tasks.query().filter_existing(tied)

    def reviewed_ids(self, tasks: list[Task]) -> frozenset[int]:
        waiting = {task_id for task_id, refs in self.tasks.open_wait_refs(tasks).items() if any(ref.type in REVIEWS for ref in refs)}
        finished = {link.target.id for link in self.links.model_links("target", tasks, FINISHED_LINK)}
        held = {link.target.id for link in self.links.model_links("target", tasks, CURRENT_TASK_LINK) if link.source.type == Worker.table() and self.workers.find(link.source.id).state == WorkerState.DELIVERED}
        return frozenset(waiting | finished | held)

    def board_names(self, plan: Plan) -> list[str]:
        standings = self.links.selected(self.links.query().filter(source=Ref.build(plan)).filter_listed("link_type", list(BOARD_LINKS.values())))
        return [row.name for row in self.numbered(link.target.id for link in standings)]

    def standing_links(self, plan: Plan, row: DomainRow) -> list[Link]:
        return self.links.selected(self.links.query().filter(source=Ref.build(plan), target=Ref.build(row)).filter_listed("link_type", list(BOARD_LINKS.values())).order("id"))

    def standing(self, plan: Plan, row: DomainRow) -> BoardPhase | None:
        kinds = {link.link_type for link in self.standing_links(plan, row)}
        return next((phase for phase, kind in BOARD_LINKS.items() if kind in kinds), None)
