from threading import RLock

from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_instances import RoleInstances
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.links import Links
from journal.repositories.tasks import QUEUED_LINK
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.rejection import Rejection


class RoleQueue:
    """Queue a shared Role's tasks one at a time per plan, keeping each plan's task order and the worker's context separate."""

    def __init__(self, instances: RoleInstances, tasks: Tasks, organization: Organization, links: Links, workers: Workers) -> None:
        self.instances, self.tasks, self.organization = instances, tasks, organization
        self.links, self.workers = links, workers
        self._feed_lock = RLock()
        self._feeding: set[int] = set()

    def queued(self, role: Role, task: Task, holder: Ref | None, actor: Actor) -> Worker:
        instance = self.instances.existing(role, task)
        if instance is None:
            raise Rejection(f"no instance of {role.title} runs yet: the main agent starts it with journal worker dispatch --role {role.id}")
        self.tasks.drop_holder(task, holder, actor)
        self.tasks.queued(task, Ref.build(instance), actor)
        return instance

    def feed(self, worker: Worker, actor: Actor) -> None:
        with self._feed_lock:
            if worker.id in self._feeding:
                return
            self._feeding.add(worker.id)
            try:
                self.feed_worker(worker, actor)
            finally:
                self._feeding.remove(worker.id)

    def feed_worker(self, worker: Worker, actor: Actor) -> None:
        current = self.workers.find(worker.id)
        role = self.organization.at(current.contract).role(current.role) if current.contract and current.role else None
        if role is None or role.cardinality is not Cardinality.JOURNAL:
            return
        queued = self.tasks.queue(Ref.build(current))
        if len(queued) < 2:
            return
        active = self.tasks.holder_task(Ref.build(current))
        last_plan = self.instances.plan_of(active) if active else current.plan_id
        if active and not last_plan:
            last_plan = current.plan_id
        ordered = self.round_robin(queued, last_plan)
        if [task.id for task in ordered] == [task.id for task in queued]:
            return
        holder = Ref.build(current)
        for link in self.links.all_matching(source=holder, link_type=QUEUED_LINK):
            self.links.delete(link, actor)
        for task in ordered:
            self.links.save(Link(source=holder, target=Ref.build(task), link_type=QUEUED_LINK), actor)

    def round_robin(self, queued: list[Task], last_plan: int) -> list[Task]:
        plans: dict[int, list[Task]] = {}
        for task in queued:
            plans.setdefault(self.instances.plan_of(task), []).append(task)
        order = sorted(plans)
        if last_plan in plans:
            start = (order.index(last_plan) + 1) % len(order)
        else:
            start = next((index for index, plan_id in enumerate(order) if plan_id > last_plan), 0)
        turns = order[start:] + order[:start]
        result = []
        while any(plans.values()):
            for plan_id in turns:
                if plans[plan_id]:
                    result.append(plans[plan_id].pop(0))
        return result
