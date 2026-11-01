from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data_reader import OrganizationDataReader
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks


class PlanTaskCompletionWake(Listener[TaskClosed]):
    """Wake the Plan seat when a completed task makes another handoff ready."""

    def __init__(self, tasks: Tasks, plans: Plans, scope: Scope, organization: Organization,
                 data: OrganizationDataReader, agents: PlanAgents, staffing: RigStaffing,
                 runtime: SeatRuntime) -> None:
        self.tasks, self.plans, self.scope = tasks, plans, scope
        self.organization, self.data, self.agents = organization, data, agents
        self.staffing, self.runtime = staffing, runtime

    def handle(self, event: TaskClosed) -> None:
        with self.scope.environment(event.environment_id):
            task = self.tasks.find(event.task_id)
            if task.state != TaskState.COMPLETED:
                return
            for plan in self.plans.started_plans(task):
                if plan.mode != PlanMode.ORGANIZATION or event.task_id not in self.plans.plan_task_ids(plan):
                    continue
                self.wake(plan)

    def wake(self, plan: Plan) -> None:
        agent = self.agents.agent(plan)
        if agent is None or not self.staffing.plan_rig_exists(plan):
            return
        waiting = self.data.waiting_plan_handoff(plan, self.organization.contracts(), "plan")
        if waiting is None:
            return
        task, domain = waiting
        rig = self.staffing.plan_rig_name(plan)
        seat = self.runtime.organization_member(rig, "plan", agent.provider)
        nudge = OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF.create(task=task, domain=domain)
        self.runtime.send(seat, nudge.rendered())
