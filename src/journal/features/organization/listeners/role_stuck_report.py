from journal.events.agent.impasse_report import ImpasseReport
from journal.events.agent_listener import AgentListener
from journal.features.organization.support.role_escalation import RoleEscalation
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class RoleStuckReport(AgentListener[ImpasseReport]):
    """A worker of a Role that says it is stuck is reported up the hub with its reason."""

    def __init__(self, escalation: RoleEscalation, workers: Workers) -> None:
        self.escalation, self.workers = escalation, workers

    def handle(self, event: ImpasseReport) -> None:
        for worker in self.workers.session_worker(event.session):
            self.escalation.report(worker, f"is stuck: {event.reason}", Actor.system())
