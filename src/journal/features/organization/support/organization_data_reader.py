from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data import OrganizationData
from journal.features.organization.support.task_part_progress import TaskPartProgress
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.features.organization.support.role_work_checks import RoleWorkChecks
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.task import Task
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.agent_role import AgentRole


class OrganizationDataReader:
    """Reads the organization feature's part of the feature data for an agent."""

    def __init__(self, organization: Organization, approvals: RoleApprovals, plan_agents: PlanAgents,
                 plans: Plans, domains: DomainRows, handoffs: OrganizationHandoffs, scope: Scope,
                 runtime: SeatRuntime, role_work_checks: RoleWorkChecks, tasks: Tasks) -> None:
        self.organization, self.approvals = organization, approvals
        self.plan_agents, self.plans, self.domains, self.handoffs, self.scope = plan_agents, plans, domains, handoffs, scope
        self.runtime, self.role_work_checks = runtime, role_work_checks
        self.tasks = tasks

    def read(self, agent: Agent) -> OrganizationData:
        contracts = self.organization.contracts()
        plan = self.plan_agents.led_plan(agent.environment_id) if agent.role == AgentRole.MAIN else None
        identity = ""
        if agent.role == AgentRole.MAIN:
            plan, identity = self.organization_seat_for_session(agent, plan)
        role_work = (
            self.role_work_checks.waiting_for_check(plan, identity.removeprefix("domain:"))
            if plan and identity.startswith("domain:") else ()
        )
        split_tasks, split_parts = self.split_work(plan, identity)
        return OrganizationData(contracts, dict(self.organization.history), self.approvals,
                                self.waiting_plan_handoff(plan, contracts, identity),
                                self.unread_domain_handoff(plan, identity), role_work, split_tasks, split_parts)

    def split_work(self, plan: Plan | None, identity: str) -> tuple[tuple[tuple[int, str], ...], tuple[TaskPartProgress, ...]]:
        if plan is None or not identity.startswith("domain:"):
            return (), ()
        domain = identity.removeprefix("domain:")
        with self.scope.environment(plan.environment_id):
            tasks = [task for task in self.plans.plan_tasks(plan) if domain in self.domains.domain_names(task)]
            split_tasks = tuple(
                (task.row_id, domain) for task in tasks
                if not task.state.is_closed() and not task.delegated and not self.tasks.parts_of(task)
            )
            split_parts = tuple(
                self.part_progress(parent, self.tasks.parts_of(parent), plan)
                for parent in tasks if self.tasks.parts_of(parent)
            )
            return split_tasks, split_parts

    def part_progress(self, parent: Task, parts: list[Task], plan: Plan) -> TaskPartProgress:
        waits = tuple(
            tuple(ref.id for ref in self.tasks.open_waits(part) if ref.type == Task.table()) for part in parts
        )
        roles = tuple(self.handoffs.latest_target(part, plan) for part in parts)
        return TaskPartProgress(
            parent.row_id, tuple(part.row_id for part in parts), roles,
            tuple(part.state for part in parts), tuple(part.delegated for part in parts), waits,
        )

    def unread_domain_handoff(self, plan: Plan | None, identity: str) -> bool:
        if plan is None or not identity.startswith("domain:"):
            return False
        with self.scope.environment(plan.environment_id):
            return any(row_plan.row_id == plan.row_id and task.state not in (TaskState.COMPLETED, TaskState.CANCELLED)
                       for _, row_plan, task in self.handoffs.pending(identity))

    def organization_seat_for_session(self, agent: Agent, plan: Plan | None) -> tuple[Plan | None, str]:
        plans = self.plans.global_matching(state=PlanState.STARTED)
        candidates = (plan, *(candidate for candidate in plans if candidate != plan)) if plan else tuple(plans)
        for candidate in candidates:
            for rig in RigStaffing.rigs_for_plan(candidate):
                identity = self.runtime.organization_seat_for_session(rig, agent.provider, agent.session)
                if identity:
                    return candidate, identity
            plan_agent = self.plan_agents.agent(candidate)
            if plan_agent and agent.session and plan_agent.session == agent.session:
                return candidate, "plan"
        return plan, ""

    def waiting_plan_handoff(self, plan: Plan | None, contracts: Contracts, identity: str) -> tuple[int, str] | None:
        if plan is None or plan.mode != PlanMode.ORGANIZATION or identity != "plan":
            return None
        with self.scope.environment(plan.environment_id):
            tasks = self.plans.plan_tasks(plan)
            preferred = self.plans.started_task(plan) or self.plans.following_task(plan)
            if preferred:
                tasks = [preferred, *(task for task in tasks if task != preferred)]
            for task in tasks:
                if task.state.is_closed():
                    continue
                domain = self.domains.planned_domain_name(task)
                if domain and contracts.domain(domain) and not self.handoffs.domain_handoff_exists(task, plan, domain):
                    return task.row_id, domain
        return None
