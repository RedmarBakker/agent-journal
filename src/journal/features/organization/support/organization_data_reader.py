from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data import OrganizationData
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
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.agent_role import AgentRole


class OrganizationDataReader:
    """Reads the organization feature's part of the feature data for an agent."""

    def __init__(self, organization: Organization, approvals: RoleApprovals, plan_agents: PlanAgents,
                 plans: Plans, domains: DomainRows, handoffs: OrganizationHandoffs, scope: Scope,
                 runtime: SeatRuntime, role_work_checks: RoleWorkChecks) -> None:
        self.organization, self.approvals = organization, approvals
        self.plan_agents, self.plans, self.domains, self.handoffs, self.scope = plan_agents, plans, domains, handoffs, scope
        self.runtime, self.role_work_checks = runtime, role_work_checks

    def read(self, agent: Agent) -> OrganizationData:
        contracts = self.organization.contracts()
        plan = self.plan_agents.led_plan(agent.environment_id) if agent.role == AgentRole.MAIN else None
        identity = ""
        if agent.role == AgentRole.MAIN:
            plan, identity = self.organization_seat_for_session(agent, plan)
        role_work = (
            self.role_work_checks.waiting_for_check(agent.session, plan, identity.removeprefix("domain:"))
            if plan and identity.startswith("domain:") else ()
        )
        return OrganizationData(contracts, dict(self.organization.history), self.approvals,
                                self.waiting_plan_handoff(plan, contracts, identity),
                                self.unread_domain_handoff(plan, identity), role_work)

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
        return plan, ""

    def waiting_plan_handoff(self, plan: Plan | None, contracts: Contracts, identity: str) -> tuple[int, str] | None:
        if plan is None or plan.mode != PlanMode.ORGANIZATION or identity not in ("", "plan"):
            return None
        with self.scope.environment(plan.environment_id):
            task = self.plans.started_task(plan) or self.plans.following_task(plan)
            if task is None:
                task = self.plans.first_planned(
                    plan, self.plans.plan_task_query(plan).filter(state=TaskState.OPEN, delegated=True),
                )
            if task is None:
                return None
            domain = self.domains.planned_domain_name(task)
            if not domain or contracts.domain(domain) is None or self.handoffs.domain_handoff_exists(task, plan, domain):
                return None
        return task.row_id, domain
