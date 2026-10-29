from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.role_policy import RolePolicy
from journal.features.workers.workers_part import WorkersPart


class RoleConduct(Conduct):
    """A worker dispatched to a Role is held from writes it cannot make and approval-required actions until one current approval lets the action through once."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        organization = event.data.part(OrganizationPart)
        worker_role = next(((worker, role) for worker in event.data.part(WorkersPart).session_workers if worker.role and (role := organization.contracts_at(worker.contract).role(worker.role))), None)
        worker, role = worker_role if worker_role else (None, None)
        refusal = RolePolicy().refusal(role, event.call) if role else None
        if refusal is None:
            return self.none()
        if refusal.key != OrganizationNudges.ACTION_WAITS_FOR_USER.key or role is None or worker is None:
            return self.refuse(refusal)
        approvals = organization.approvals
        return self.none() if approvals and approvals.authorizes_worker(event.session, worker, role, event.call) else self.refuse(refusal)
