from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.organization_handoff import OrganizationHandoff
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.scope import Scope
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

TASK_HANDOFF = "organization_handoff_task"
PLAN_HANDOFF = "organization_handoff_plan"


class OrganizationHandoffs(ScopedRepository[OrganizationHandoff]):
    """Tasks handed through the organization's routes, addressed to one generated seat."""

    model = OrganizationHandoff

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, tasks: Tasks, plans: Plans, time_source: TimeSource) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.links, self.tasks, self.plans = links, tasks, plans

    def handoff(self, task: Task, plan: Plan, target: str, actor: Actor) -> OrganizationHandoff:
        for row, existing_plan, existing in self.pending(target):
            if existing_plan.row_id == plan.row_id and existing.row_id == task.row_id:
                return row
        row = self.save(OrganizationHandoff(target=target), actor)
        self.links.linked(Ref.build(row), Ref.build(task), TASK_HANDOFF, actor)
        self.links.linked(Ref.build(row), Ref.build(plan), PLAN_HANDOFF, actor)
        return row

    def pending(self, target: str) -> tuple[tuple[OrganizationHandoff, Plan, Task], ...]:
        rows = self.selected(self.query().filter(target=target).filter_null("read_at").order("id"))
        result = []
        for row in rows:
            task_refs, plan_refs = self.links.targets(row, TASK_HANDOFF), self.links.targets(row, PLAN_HANDOFF)
            if task_refs and plan_refs:
                result.append((row, self.plans.find(plan_refs[0].id), self.tasks.find(task_refs[0].id)))
        return tuple(result)

    def domain_handoff_exists(self, task: Task, plan: Plan, domain: str) -> bool:
        target = f"domain:{domain}"
        task_ref, plan_ref = Ref.build(task), Ref.build(plan)
        rows = self.selected_globally(self.query().filter(target=target))
        return any(task_ref in self.links.targets(row, TASK_HANDOFF) and
                   plan_ref in self.links.targets(row, PLAN_HANDOFF)
                   for row in rows)

    def latest_target(self, task: Task, plan: Plan) -> str:
        plan_ref = Ref.build(plan)
        for reference in reversed(self.links.typed_sources(task, TASK_HANDOFF, OrganizationHandoff.table())):
            row = self.find(reference.id)
            if plan_ref in self.links.targets(row, PLAN_HANDOFF):
                return row.target
        return ""

    def reopen_domain_inboxes(self, plan: Plan, actor: Actor) -> None:
        with self.scope.environment(plan.environment_id):
            unfinished = {task.row_id for task in self.plans.plan_tasks(plan) if not task.state.is_closed()}
            latest: dict[int, OrganizationHandoff] = {}
            for ref in self.links.typed_sources(plan, PLAN_HANDOFF, OrganizationHandoff.table()):
                row = self.find(ref.id)
                if not row.target.startswith("domain:"):
                    continue
                task_refs = self.links.targets(row, TASK_HANDOFF)
                if task_refs and task_refs[0].id in unfinished:
                    task_id = task_refs[0].id
                    if task_id not in latest or row.row_id > latest[task_id].row_id:
                        latest[task_id] = row
            for row in latest.values():
                if row.read_at is not None:
                    self.save(row.unread(), actor)

    def unread_in_plan(self, plan: Plan, target: str) -> bool:
        plan_ref = Ref.build(plan)
        rows = self.selected_globally(self.query().filter(target=target).filter_null("read_at"))
        return any(plan_ref in self.links.targets(row, PLAN_HANDOFF) for row in rows)

    def in_plan(self, rows: tuple[tuple[OrganizationHandoff, Plan, Task], ...], plan: Plan) -> tuple[tuple[OrganizationHandoff, Plan, Task], ...]:
        return tuple(row for row in rows if row[1].row_id == plan.row_id)

    def read(self, row: OrganizationHandoff, actor: Actor) -> OrganizationHandoff:
        return self.save(row.read(self.time_source.moment()), actor)
