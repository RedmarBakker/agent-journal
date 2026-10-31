from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_reopened import TaskReopened
from journal.engine.nudge import Nudge
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks


class SplitPartWake(Listener[RowEvent]):
    """Wake the Domain seat when one of its split parts is ready or its split task changes."""

    def __init__(self, tasks: Tasks, plans: Plans, handoffs: OrganizationHandoffs,
                 agents: PlanAgents, runtime: SeatRuntime, staffing: RigStaffing) -> None:
        self.tasks, self.plans, self.handoffs = tasks, plans, handoffs
        self.agents, self.runtime, self.staffing = agents, runtime, staffing

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, TaskReopened):
            self.ready(event.task_id)
        if isinstance(event, TaskClosed):
            self.closed(event.task_id)

    def ready(self, task_id: int) -> None:
        context = self.part_context(task_id)
        if context is None:
            return
        task, _, plan = context
        if task.state != TaskState.OPEN or task.delegated or self.tasks.open_waits(task):
            return
        domain, role = self.role_target(task, plan)
        if domain and role:
            self.wake(plan, domain, OrganizationNudges.SPLIT_PART_READY.create(task=task.id, role=role))

    def closed(self, task_id: int) -> None:
        context = self.part_context(task_id)
        if context is None:
            return
        task, parent, plan = context
        parts = self.tasks.parts_of(parent)
        if all(part.state == TaskState.CANCELLED for part in parts):
            self.wake(plan, self.domain_target(parent, plan),
                      OrganizationNudges.SPLIT_ALL_PARTS_CANCELLED.create(task=parent.id))

    def completed(self, task_id: int) -> None:
        context = self.part_context(task_id)
        if context is None:
            return
        task, parent, plan = context
        if all(part.state == TaskState.COMPLETED for part in self.tasks.parts_of(parent)):
            self.wake(plan, self.domain_target(parent, plan),
                      OrganizationNudges.SPLIT_TASK_COMPLETED.create(task=parent.id))

    def part_context(self, task_id: int) -> tuple[Task, Task, Plan] | None:
        task = self.tasks.find(task_id)
        parent = self.tasks.part_of_task(task)
        if parent is None:
            return None
        plans = self.plans.containing(parent)
        if len(plans) != 1:
            return None
        return task, parent, plans[0]

    def role_target(self, task: Task, plan: Plan) -> tuple[str, str]:
        target = self.handoffs.latest_target(task, plan)
        if not target.startswith("role:"):
            return "", ""
        domain, _, role = target.removeprefix("role:").partition("/")
        return (domain, target) if role else ("", "")

    def domain_target(self, task: Task, plan: Plan) -> str:
        target = self.handoffs.latest_target(task, plan)
        if target.startswith("domain:"):
            return target.removeprefix("domain:")
        if target.startswith("role:"):
            domain, _, _ = target.removeprefix("role:").partition("/")
            return domain
        return ""

    def wake(self, plan: Plan, domain: str, nudge: Nudge) -> None:
        if not domain or plan.state not in (PlanState.STARTED, PlanState.DELEGATED) or not (agent := self.agents.agent(plan)):
            return
        rig = self.staffing.plan_rig_name(plan)
        seat = self.runtime.organization_member(rig, f"domain:{domain}", agent.provider)
        self.runtime.send(seat, nudge.rendered())
