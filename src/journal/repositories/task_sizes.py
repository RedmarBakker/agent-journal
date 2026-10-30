from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.features.estimates.support.task_size_scale import TaskSizeScale
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.plans.support.plan_owners import PlanOwners
from journal.models.agent import ENDED_STATE
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_size_estimate import TaskSizeEstimate
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.sprints import Sprints
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

TASK_SIZE_LINK = "task_size_estimate"


class TaskSizes(ScopedRepository[TaskSizeEstimate]):
    """The checked writer and read projection for immutable task size history."""

    model = TaskSizeEstimate

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource, tasks: Tasks, plans: Plans,
                 links: Links, owners: PlanOwners, plan_agents: PlanAgents, agents: Agents, scale: TaskSizeScale, sprints: Sprints) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.tasks, self.plans, self.links, self.owners = tasks, plans, links, owners
        self.plan_agents, self.agents, self.scale, self.sprints = plan_agents, agents, scale, sprints

    def save(self, row: TaskSizeEstimate, actor: Actor) -> TaskSizeEstimate:
        if not row.is_new:
            raise Rejection("task size history is immutable")
        return super().save(row, actor)

    def delete(self, row: TaskSizeEstimate, actor: Actor) -> None:
        raise Rejection("task size history is immutable")

    def compose(self, plan: Plan, task: Task, value: object, actor: Actor) -> Task:
        self.builder(plan, actor)
        size, version = self.scale.parse_with_version(value)
        with self.writing():
            saved = self.tasks.save(task.with_(size=size), actor)
            self._append(saved, "planning_baseline", size, "plan composition", version, actor)
            return saved

    def revise(self, task_id: int, value: object, reason: str, actor: Actor) -> Task:
        return self.rewrite(task_id, value, reason, "size_revision", actor)

    def revise_scope(self, task_id: int, value: object, reason: str, actor: Actor) -> Task:
        return self.rewrite(task_id, value, reason, "scope_revision", actor)

    def rewrite(self, task_id: int, value: object, reason: str, change_type: str, actor: Actor) -> Task:
        task = self.tasks.find(task_id)
        plan = self.task_plan(task)
        self.builder(plan, actor)
        if not isinstance(reason, str) or not reason.strip():
            raise Rejection("a size revision needs a reason")
        size, version = self.scale.parse_with_version(value)
        with self.writing():
            saved = self.tasks.save(task.with_(size=size), actor)
            self._append(saved, change_type, size, reason.strip(), version, actor)
            return saved

    def propose(self, task_id: int, value: object, reason: str, actor: Actor) -> TaskSizeEstimate:
        task = self.tasks.find(task_id)
        if actor.actor_type != ActorType.WORKER or self.tasks.holder(task) != Ref(Worker.table(), actor.number()):
            raise Rejection("only the worker holding this task may propose a size revision")
        if not isinstance(reason, str) or not reason.strip():
            raise Rejection("a resize proposal needs a reason")
        size, version = self.scale.parse_with_version(value)
        if not task.is_active():
            raise Rejection("a worker may propose a resize only while it is working on the task")
        with self.writing():
            return self._append(task, "resize_proposal", size, reason.strip(), version, actor)

    def first_ready(self, plan_id: int, actor_stamp: str) -> None:
        plan = self.plans.find(plan_id)
        actor = Actor.parse(actor_stamp)
        version = self.scale.version()
        with self.writing():
            for task in self.plans.plan_tasks(plan):
                if not any(row.change_type == "first_ready" for row in self.history(task)):
                    self._append(task, "first_ready", task.size, "plan first marked ready", version, actor)

    def show(self, task_id: int) -> dict:
        task = self.tasks.find(task_id)
        rows = self.history(task)
        baseline = self.first(rows, "planning_baseline")
        ready = self.first(rows, "first_ready")
        committed = self.sprint_commitment(task)
        accepted = [self.history_data(row) for row in rows if row.change_type != "resize_proposal"]
        proposals = [self.history_data(row) for row in rows if row.change_type == "resize_proposal"]
        return {"task_id": task.row_id, "current_size": task.size, "current_scale_version": self.scale.version(),
                "planning_baseline_size": baseline.size if baseline else None,
                "first_ready_size": ready.size if ready else None,
                "first_ready_scale_version": ready.scale_version if ready else None,
                "sprint_committed_size": committed.get("size") if committed else None,
                "sprint_committed_scale_version": committed.get("size_scale_version") if committed else None,
                "history": accepted, "proposal_history": proposals}

    def sprint_commitment(self, task: Task) -> dict | None:
        for ref in self.links.targets(task, PLAN_LINK):
            if ref.type == Plan.table():
                snapshot = self.sprints.committed_task_snapshot(self.plans.find(ref.id), task.row_id)
                if snapshot is not None:
                    return snapshot
        return None

    def history(self, task: Task) -> list[TaskSizeEstimate]:
        return [self.find(ref.id) for ref in self.links.typed_targets(task, TASK_SIZE_LINK, TaskSizeEstimate.table())]

    def _append(self, task: Task, change_type: str, size: int | None, reason: str, scale_version: str, actor: Actor) -> TaskSizeEstimate:
        row = self.save(TaskSizeEstimate(environment_id=task.environment_id, change_type=change_type, size=size, reason=reason, scale_version=scale_version), actor)
        self.links.linked(Ref.build(task), Ref.build(row), TASK_SIZE_LINK, actor)
        return row

    def builder(self, plan: Plan, actor: Actor) -> None:
        if actor.actor_type == ActorType.USER and self.owners.number(plan) == actor.number():
            return
        if actor.actor_type == ActorType.AGENT and not actor.is_subagent():
            session = actor.agent_session()
            active = self.agents.active_main_agent(session)
            if plan.state.is_unapproved() and active and active.environment_id == plan.environment_id:
                return
            plan_agent = self.plan_agents.agent(plan)
            if plan.state in (PlanState.STARTED, PlanState.DELEGATED) and plan_agent and plan_agent.state != ENDED_STATE and plan_agent.session == session:
                return
        raise Rejection(f"only the plan owner or active plan builder may set task sizes for plan {plan.id}")

    def task_plan(self, task: Task) -> Plan:
        refs = self.links.targets(task, PLAN_LINK)
        plan_ref = next((ref for ref in refs if ref.type == Plan.table()), None)
        if plan_ref is None:
            raise Rejection(f"task {task.id} is not in a plan: only planned tasks have story point sizes")
        return self.plans.find(plan_ref.id)

    def history_data(self, row: TaskSizeEstimate) -> dict:
        return {"id": row.row_id, "change_type": row.change_type, "size": row.size, "reason": row.reason,
                "scale_version": row.scale_version, "recorded_at": row.created_at.isoformat() if row.created_at else "",
                "actor": row.creator.stamp if row.creator else ""}

    @staticmethod
    def first(rows: list[TaskSizeEstimate], change_type: str) -> TaskSizeEstimate | None:
        return next((row for row in rows if row.change_type == change_type), None)
