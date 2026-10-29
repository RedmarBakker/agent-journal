from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.support.role_policy import RolePolicy
from journal.features.workers.workers_part import WorkersPart


class RoleConduct(Conduct):
    """A worker dispatched to a Role works inside it: a write is refused when the Role has no write tool, and a command that is an action the Role lists as approval-required is refused until the user has been asked; a worker with no Role, or whose Role the folder no longer holds, is let through."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        role = next((found for worker in event.data.part(WorkersPart).session_workers if worker.role and (found := event.data.part(OrganizationPart).contracts_at(worker.contract).role(worker.role))), None)
        refusal = RolePolicy().refusal(role, event.call) if role else None
        return self.refuse(refusal) if refusal else self.none()
