from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.role_step_ended import RoleStepEnded
from journal.events.agent.role_taken import RoleTaken
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.role_policy import RolePolicy
from journal.features.organization.support.tool_ids import ToolIds
from journal.features.organization.support.role_approvals import RoleApprovalContext
from journal.features.plans.plans_part import PlansPart


@dataclass(frozen=True)
class RoleWork(BaseState):
    """A solo Plan agent acting as one Role for a step, by the Role's id and the contracts' version at the push: the Role read at that version refuses what RolePolicy refuses a worker of it, and a tool its tools do not name, a journal command never; the Role's and its domain's guidance are sent again when the state is back on top, after a compaction among others; a second Role waits for this one's end, and journal role done pops it."""

    name = "role_work"
    title = "Working as a Role"

    role: str = ""
    version: str = ""

    def subject(self) -> str:
        return f"Role {self.role}"

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        role = event.data.part(OrganizationPart).contracts_at(self.version).role(self.role)
        if role is None or event.call.is_journal:
            return self.none()
        refusal = RolePolicy().refusal(role, event.call)
        if refusal is not None and refusal.key != OrganizationNudges.ACTION_WAITS_FOR_USER.key:
            return self.refuse(refusal)
        if not role.allows_call(event.call.tool):
            return self.refuse(OrganizationNudges.ROLE_TOOL_REFUSED.create(role=role.title, tool=event.call.tool, tools=ToolIds().words(role.tools) or "none"))
        if refusal is None:
            return self.none()
        organization = event.data.part(OrganizationPart)
        started = event.data.part(PlansPart).started
        approvals = organization.approvals
        if started and started.plan_id and started.started_task and event.environment_id and approvals:
            context = RoleApprovalContext(event.session, role.id, started.plan_id, started.started_task, event.environment_id)
            if approvals.authorizes(context, role, event.call):
                return self.none()
        return self.refuse(refusal)

    def on_role_taken(self, event: RoleTaken, settings: Settings) -> Transition:
        return self.none(OrganizationNudges.ONE_ROLE_AT_A_TIME.create(role=self.role))

    def on_role_step_ended(self, event: RoleStepEnded, settings: Settings) -> Transition:
        return self.pop()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        return self.guidance(data.part(OrganizationPart).contracts_at(self.version))

    def guidance(self, contracts: Contracts) -> tuple[Nudge, ...]:
        role = contracts.role(self.role)
        if role is None:
            return ()
        domain = contracts.domain(role.domain)
        return (OrganizationNudges.ACTING_AS_ROLE.create(role=role.title, guidance="\n\n".join(text for text in (domain.guidance if domain else "", role.guidance) if text)),)
