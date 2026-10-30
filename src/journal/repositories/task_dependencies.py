from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_log import TaskLog
from journal.repositories.delivery_records import DeliveryRecords
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.task_logs import TaskLogs
from journal.repositories.task_sizes import TaskSizes
from journal.repositories.tasks import DEPENDENCY_LINK, DELIVERY_GATE_LINK, Tasks
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class TaskDependencies:
    """The checked writer and read projection for planned task prerequisites and delivery gates."""

    def __init__(self, tasks: Tasks, plans: Plans, links: Links, sizes: TaskSizes, logs: TaskLogs, delivery: DeliveryRecords, time_source: TimeSource) -> None:
        self.tasks, self.plans, self.links, self.sizes, self.logs, self.delivery, self.time_source = tasks, plans, links, sizes, logs, delivery, time_source

    def prepare_composition(self, plan: Plan, prerequisite_ids: object, gate_target_id: object, reason: object, actor: Actor) -> None:
        prerequisites = self.numbered_ids(prerequisite_ids)
        gate_target = self.optional_id(gate_target_id)
        if not prerequisites and not gate_target:
            return
        self.authorize(plan, actor)
        if (prerequisites or gate_target) and not self.reason_text(reason):
            raise Rejection("planned prerequisites and delivery gates need a reason")
        self.prerequisite_tasks(prerequisites)
        if gate_target:
            self.validate_delivery_gate_target(gate_target)

    def compose(self, task: Task, prerequisite_ids: object, gate_target_id: object, reason: object, actor: Actor) -> None:
        prerequisites, gate_target = self.numbered_ids(prerequisite_ids), self.optional_id(gate_target_id)
        if not prerequisites and not gate_target:
            return
        plan = self.sizes.task_plan(task)
        self.prepare_composition(plan, prerequisites, gate_target, reason, actor)
        self.write(task, prerequisites, gate_target, self.reason_text(reason), actor)

    def replace(self, task_id: int, prerequisite_ids: object, reason: object, actor: Actor) -> None:
        task = self.tasks.find(task_id)
        plan = self.sizes.task_plan(task)
        self.replace_in_plan(plan, task, prerequisite_ids, reason, actor)

    def replace_in_plan(self, plan: Plan, task: Task, prerequisite_ids: object, reason: object, actor: Actor) -> None:
        self.authorize(plan, actor)
        if not any(link.link_type == PLAN_LINK for link in self.links.connecting(task, plan)):
            raise Rejection(f"task {task.id} is not in plan {plan.id}")
        prerequisites = self.numbered_ids(prerequisite_ids)
        reason_text = self.reason_text(reason)
        if not reason_text:
            raise Rejection("changing planned prerequisites needs a reason")
        if task.delegated or self.tasks.task_worker_holdings({task.row_id}):
            holder = self.tasks.holder(task)
            raise Rejection(f"task {task.id} is worker {holder.id if holder else 'unknown'}'s: revise planned prerequisites before the worker takes it")
        if task.started_at is not None or task.is_closed():
            raise Rejection(f"planned prerequisites for task {task.id} must be set before it starts")
        self.prerequisite_tasks(prerequisites)
        if task.row_id in prerequisites:
            raise Rejection("a task cannot depend on itself: that would close a cycle")
        self.write(task, prerequisites, 0, reason_text, actor)

    def authorize(self, plan: Plan, actor: Actor) -> None:
        self.sizes.builder(plan, actor)

    def show(self, plan: Plan) -> dict:
        tasks = self.plans.plan_tasks(plan)
        links = self.links.model_links("source", tasks, DEPENDENCY_LINK)
        task_ids = {task.row_id for task in tasks}
        edges = [{"task_id": link.source.id, "prerequisite_id": link.target.id}
                 for link in links if link.source.id in task_ids and link.target.type == Task.table()]
        return {"plan_id": plan.row_id, "edges": edges}

    def require_delivery_evidence(self, gate: Task) -> None:
        refs = self.links.typed_targets(gate, DELIVERY_GATE_LINK, Task.table())
        for ref in refs:
            target = self.tasks.find(ref.id)
            if not self.delivery.accepted_for_task(target):
                raise Rejection(f"delivery gate task {gate.id} needs accepted delivery evidence for task {target.id} before it can be completed")

    def validate_delivery_gate_target(self, task_id: int) -> None:
        if self.delivery.mode() == "off":
            raise Rejection("a delivery gate needs estimates mode record, report or enforce")
        task = self.tasks.find(task_id)
        policies = [self.delivery.policy(self.plans.find(ref.id), task) for ref in self.links.targets(task, PLAN_LINK) if ref.type == Plan.table()]
        if not any(domain and definition and version for domain, definition, version in policies):
            raise Rejection(f"task {task.id} needs a planned domain with a definition of done before it can have a delivery gate")

    def prerequisite_tasks(self, prerequisite_ids: list[int]) -> list[Task]:
        if len(set(prerequisite_ids)) != len(prerequisite_ids):
            raise Rejection("planned prerequisites repeat a task")
        return [self.tasks.find(task_id) for task_id in prerequisite_ids]

    def write(self, task: Task, prerequisite_ids: list[int], gate_target_id: int, reason: str, actor: Actor) -> None:
        with self.links.writing():
            for link in self.links.source_links(task, DEPENDENCY_LINK):
                self.links.delete(link, actor)
            for task_id in prerequisite_ids:
                prerequisite = self.tasks.find(task_id)
                self.links.save(Link(source=Ref.build(task), target=Ref.build(prerequisite), link_type=DEPENDENCY_LINK), actor)
            if gate_target_id:
                self.links.save(Link(source=Ref.build(task), target=Ref(Task.table(), gate_target_id), link_type=DELIVERY_GATE_LINK), actor)
            self.logs.save(TaskLog.build(task, self.reason_line(prerequisite_ids, gate_target_id, reason), self.time_source.moment().timestamp()), actor)

    @staticmethod
    def reason_line(prerequisite_ids: list[int], gate_target_id: int, reason: str) -> str:
        conditions = [f"prerequisites: {', '.join(map(str, prerequisite_ids))}" if prerequisite_ids else "prerequisites cleared"]
        if gate_target_id:
            conditions.append(f"delivery gate for task {gate_target_id}")
        return f"planned {' and '.join(conditions)}: {reason}"

    @staticmethod
    def numbered_ids(values: object) -> list[int]:
        if values is None:
            return []
        if not isinstance(values, list) or any(not isinstance(value, int) or isinstance(value, bool) or value < 1 for value in values):
            raise Rejection("planned prerequisites must be a list of task numbers")
        return list(values)

    @staticmethod
    def optional_id(value: object) -> int:
        if value is None or value == "":
            return 0
        if isinstance(value, int) and not isinstance(value, bool) and value == 0:
            return 0
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise Rejection("a delivery gate target must be a task number")
        return value

    @staticmethod
    def reason_text(value: object) -> str:
        return value.strip() if isinstance(value, str) else ""
