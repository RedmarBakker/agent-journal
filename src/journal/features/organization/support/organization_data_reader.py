from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data import OrganizationData
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.models.agent import Agent
from journal.models.plan_mode import PlanMode
from journal.models.task_state import TaskState
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.organization.support.contracts import Contracts


class OrganizationDataReader:
    """Reads the organization feature's part of the feature data for an agent."""

    def __init__(self, organization: Organization, approvals: RoleApprovals, plan_agents: PlanAgents,
                 plans: Plans, domains: DomainRows, handoffs: OrganizationHandoffs, scope: Scope) -> None:
        self.organization, self.approvals = organization, approvals
        self.plan_agents, self.plans, self.domains, self.handoffs, self.scope = plan_agents, plans, domains, handoffs, scope

    def read(self, agent: Agent) -> OrganizationData:
        contracts = self.organization.contracts()
        return OrganizationData(contracts, dict(self.organization.history), self.approvals,
                                self.waiting_plan_handoff(agent, contracts))

    def waiting_plan_handoff(self, agent: Agent, contracts: Contracts) -> tuple[int, str] | None:
        plan = self.plan_agents.led_plan(agent.environment_id)
        if plan is None or plan.mode != PlanMode.ORGANIZATION:
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
