from journal.events.listener import Listener
from journal.events.rows.worker_unfinished import WorkerUnfinished
from journal.features.organization.support.role_escalation import RoleEscalation
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class RoleEndingReport(Listener[WorkerUnfinished]):
    """A worker of a Role whose run ended without clocking out, as when it timed out, is reported up the hub with how its run ended."""

    def __init__(self, escalation: RoleEscalation, workers: Workers) -> None:
        self.escalation, self.workers = escalation, workers

    def handle(self, event: WorkerUnfinished) -> None:
        worker = self.workers.find(event.worker.id)
        self.escalation.report(worker, f"ended without clocking out: {worker.run_end}", Actor.system())
