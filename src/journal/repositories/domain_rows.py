from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.models.agent import Agent
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
DOMAIN_AGENT_LINK = "domain_agent"
PLANNED_DOMAIN_LINK = "planned_domain"
DOMAIN_HISTORY_LINK = "domain_history"
BOARD_LINKS = {phase: f"on_board_{phase.value}" for phase in BoardPhase}
REVIEWS = (Check.table(), Question.table())


class DomainRows(Repository[DomainRow]):
    """The organization domains that tasks are planned for and handed to, retaining the first planned domain and later handoffs; and each plan's domain-board phase."""

    model = DomainRow

    def __init__(self, connection: Connection, bus: Bus, links: Links, tasks: Tasks, workers: Workers, time_source: TimeSource) -> None:
        super().__init__(connection, bus, time_source)
        self.links, self.tasks, self.workers = links, tasks, workers

    def task_tied(self, task: Task, name: str, actor: Actor) -> Link:
        with self.writing():
            domain = Ref.build(self.named(name, actor))
            source = Ref.build(task)
            planned = self.links.targets(task, PLANNED_DOMAIN_LINK)
            current = self.links.targets(task, DOMAIN_LINK)
            if not planned:
                first = current[-1] if current else domain
                self.links.linked(source, first, PLANNED_DOMAIN_LINK, actor)
                if current:
                    self.links.linked(source, first, DOMAIN_HISTORY_LINK, actor)
            if not current or current[-1] != domain:
                self.links.save(Link(source=source, target=domain, link_type=DOMAIN_HISTORY_LINK), actor)
                for link in self.links.all_matching(source=source, link_type=DOMAIN_LINK):
                    self.links.delete(link, actor)
            return self.links.linked(Ref.build(task), domain, DOMAIN_LINK, actor)

    def named(self, name: str, actor: Actor) -> DomainRow:
        with self.writing():
            rows = self.all_matching(name=name)
            return rows[0] if rows else self.save(DomainRow(name=name), actor)

    def domain_names(self, task: Task) -> list[str]:
        return [row.name for row in self.numbered(ref.id for ref in self.links.targets(task, DOMAIN_LINK))]

    def planned_domain_name(self, task: Task) -> str | None:
        planned = self.links.targets(task, PLANNED_DOMAIN_LINK)
        domain = planned[0] if planned else next(iter(self.links.targets(task, DOMAIN_LINK)), None)
        return self.find(domain.id).name if domain else None

    def domain_history(self, task: Task) -> list[str]:
        return [self.find(ref.id).name for ref in self.links.targets(task, DOMAIN_HISTORY_LINK)]

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
        held = {link.target.id for link in self.links.model_links("target", tasks, CURRENT_TASK_LINK)
                if link.source.type == Worker.table()
                and self.workers.global_matching(id=link.source.id)[0].state == WorkerState.DELIVERED}
        return frozenset(waiting | finished | held)

    def board_names(self, plan: Plan) -> list[str]:
        standings = self.links.selected(self.links.query().filter(source=Ref.build(plan)).filter_listed("link_type", list(BOARD_LINKS.values())))
        return [row.name for row in self.numbered(link.target.id for link in standings)]

    def standing_links(self, plan: Plan, row: DomainRow) -> list[Link]:
        return self.links.selected(self.links.query().filter(source=Ref.build(plan), target=Ref.build(row)).filter_listed("link_type", list(BOARD_LINKS.values())).order("id"))

    def standing(self, plan: Plan, row: DomainRow) -> BoardPhase | None:
        kinds = {link.link_type for link in self.standing_links(plan, row)}
        return next((phase for phase, kind in BOARD_LINKS.items() if kind in kinds), None)

    def agent_linked(self, name: str, agent: Agent, actor: Actor) -> Link:
        return self.links.linked(Ref.build(self.named(name, actor)), Ref.build(agent), DOMAIN_AGENT_LINK, actor)

    def agent_id(self, name: str) -> int:
        rows = self.all_matching(name=name)
        return next((ref.id for ref in self.links.targets(rows[0], DOMAIN_AGENT_LINK)), 0) if rows else 0
