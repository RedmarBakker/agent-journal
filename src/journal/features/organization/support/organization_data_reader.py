from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data import OrganizationData
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.task_state import TaskState
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.rigs import Rigs
from journal.repositories.scope import Scope
from journal.support.agent_role import AgentRole


class OrganizationDataReader:
    """Reads the organization feature's part of the feature data for an agent."""

    def __init__(self, organization: Organization, approvals: RoleApprovals, plan_agents: PlanAgents,
                 plans: Plans, domains: DomainRows, handoffs: OrganizationHandoffs, scope: Scope,
                 rigs: Rigs, runtime: SeatRuntime) -> None:
        self.organization, self.approvals = organization, approvals
        self.plan_agents, self.plans, self.domains, self.handoffs, self.scope = plan_agents, plans, domains, handoffs, scope
        self.rigs, self.runtime = rigs, runtime

    def read(self, agent: Agent) -> OrganizationData:
        contracts = self.organization.contracts()
        plan = self.plan_agents.led_plan(agent.environment_id) if agent.role == AgentRole.MAIN else None
        identity = self.organization_seat_for_session(plan, agent) if plan and plan.mode == PlanMode.ORGANIZATION else ""
        return OrganizationData(contracts, dict(self.organization.history), self.approvals,
                                self.waiting_plan_handoff(plan, contracts, identity), self.unread_domain_handoff(plan, identity))

    def unread_domain_handoff(self, plan: Plan | None, identity: str) -> bool:
        if plan is None or not identity.startswith("domain:"):
            return False
        with self.scope.environment(plan.environment_id):
            return bool(self.handoffs.pending(identity))

    def organization_seat_for_session(self, plan: Plan, agent: Agent) -> str:
        rig_id = self.plans.rig_id(plan)
        rig_names = [self.rigs.find(rig_id).name] if rig_id else []
        shared = self.rigs.global_matching(
            name=RigStaffing.shared_rig_name(plan.environment_id), environment_id=plan.environment_id,
        )
        rig_names.extend(rig.name for rig in shared)
        return next((identity for rig in rig_names
                     if (identity := self.runtime.organization_seat_for_session(rig, agent.provider, agent.session))), "")

    def waiting_plan_handoff(self, plan: Plan | None, contracts: Contracts, identity: str) -> tuple[int, str] | None:
        if plan is None or plan.mode != PlanMode.ORGANIZATION or identity not in ("", "plan"):
            return None
        with self.scope.environment(plan.environment_id):
            task = self.plans.started_task(plan) or self.plans.following_task(plan)
            task = task or next((candidate for candidate in self.plans.plan_tasks(plan)
                                 if candidate.state == TaskState.OPEN and candidate.delegated), None)
            if task is None:
                return None
            domain = self.domains.planned_domain_name(task)
        if not domain or contracts.domain(domain) is None:
            return None
        handed_off = self.handoffs.domain_handoff_exists(task, plan, domain)
        if handed_off:
            return None
        return task.row_id, domain
