from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.tasks import PART_LINK, PLAN_LINK, WAIT_LINK, Tasks
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class TaskParts:
    """Creates Role parts and cross-Domain tasks for a plan task."""

    def __init__(self, tasks: Tasks, links: Links, domains: DomainRows, plans: Plans,
                 time_source: TimeSource) -> None:
        self.tasks, self.links, self.domains, self.plans = tasks, links, domains, plans
        self.time_source = time_source

    def part(self, parent: Task, plan: Plan, domain: str, title: str, brief: str,
             after: int, actor: Actor) -> Task:
        self.require_parent(parent, plan)
        previous = self.predecessor(parent, after)
        task = self.tasks.save(Task(environment_id=parent.environment_id, title=title, brief=brief), actor)
        self.links.linked(Ref.build(task), Ref.build(parent), PART_LINK, actor)
        self.domains.task_tied(task, domain, actor)
        if previous:
            wait = Link(source=Ref.build(task), target=Ref.build(previous), link_type=WAIT_LINK)
            self.tasks.require_acyclic_link(wait)
            self.links.save(wait, actor)
            return self.tasks.save(task.blocked(f"after task {previous.id}", self.time_source.moment()), actor)
        return task

    def other(self, parent: Task, plan: Plan, domain: str, title: str, brief: str, actor: Actor) -> Task:
        self.require_parent(parent, plan)
        task = self.tasks.save(Task(environment_id=plan.environment_id, title=title, brief=brief), actor)
        self.links.linked(Ref.build(task), Ref.build(parent), PART_LINK, actor)
        self.links.linked(Ref.build(task), Ref.build(plan), PLAN_LINK, actor)
        self.domains.task_tied(task, domain, actor)
        return task

    def require_parent(self, parent: Task, plan: Plan) -> None:
        if self.tasks.part_of_task(parent):
            raise Rejection(f"task {parent.id} is a part: parts cannot have their own parts")
        if parent not in self.plans.plan_tasks(plan):
            raise Rejection(f"task {parent.id} is not in a plan")
        if parent.state.is_closed():
            raise Rejection(f"task {parent.id} is closed and cannot have parts")
        if parent.delegated:
            raise Rejection(self.tasks.delegated_refusal(parent))

    def predecessor(self, parent: Task, task_id: int) -> Task | None:
        if not task_id:
            return None
        previous = self.tasks.find(task_id)
        if self.tasks.part_of_task(previous) != parent:
            raise Rejection(f"task {task_id} is not a part of task {parent.id}; --after must name one of its parts")
        return previous
