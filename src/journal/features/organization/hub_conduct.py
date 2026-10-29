from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.role_escalated import RoleEscalated
from journal.features.organization.organization_nudges import OrganizationNudges


class HubConduct(Conduct):
    """An agent up the hub, a Domain agent or a Plan agent, is told the report of a Role that was sent to it."""

    def on_role_escalated(self, event: RoleEscalated, settings: Settings) -> Transition:
        return self.none(OrganizationNudges.ROLE_REPORTED.create(report=event.report)) if event.recipient == event.session else self.none()
