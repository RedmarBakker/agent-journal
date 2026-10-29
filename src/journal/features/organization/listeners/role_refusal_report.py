from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.role_escalation import RoleEscalation
from journal.repositories.workers import Workers
from journal.support.actor import Actor

REFUSALS = {nudge.key: nudge for nudge in (OrganizationNudges.ROLE_WRITES_NOTHING, OrganizationNudges.ACTION_WAITS_FOR_USER)}


class RoleRefusalReport(AgentListener[LineDelivered]):
    """A worker refused what its Role does not allow is reported up the hub with the line it was refused with."""

    def __init__(self, escalation: RoleEscalation, workers: Workers) -> None:
        self.escalation, self.workers = escalation, workers

    def handle(self, event: LineDelivered) -> None:
        if event.nudge not in REFUSALS:
            return
        refusal = REFUSALS[event.nudge].create(**event.values).rendered()
        for worker in self.workers.session_worker(event.session):
            self.escalation.report(worker, "was refused", refusal, Actor.system())
