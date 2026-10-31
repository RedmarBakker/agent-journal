from journal.events.listener import Listener
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.role_work_checks import RoleWorkChecks
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.repositories.plans import Plans
from journal.repositories.workers import Workers


class RoleClockOutWake(Listener[WorkerDelivered]):
    """Wake the Domain seat that sent a Role worker when its work is ready to check."""

    def __init__(self, workers: Workers, plans: Plans, checks: RoleWorkChecks, runtime: SeatRuntime) -> None:
        self.workers, self.plans, self.checks, self.runtime = workers, plans, checks, runtime

    def handle(self, event: WorkerDelivered) -> None:
        if not event.task_id:
            return
        worker = self.workers.find(event.worker.id)
        if not worker.plan_id or not worker.role or not worker.dispatcher:
            return
        plans = self.plans.global_matching(id=worker.plan_id)
        if not plans:
            return
        plan = plans[0]
        for rig in RigStaffing.rigs_for_plan(plan):
            identity = self.runtime.organization_seat_for_session(rig, worker.provider, worker.dispatcher)
            if not identity.startswith("domain:"):
                continue
            domain = identity.removeprefix("domain:")
            if not self.checks.is_waiting_for_check(worker, event.task_id, plan, domain):
                continue
            recipient = self.runtime.organization_member(rig, identity, worker.provider)
            nudge = OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=worker.id, task=event.task_id)
            self.runtime.send(recipient, nudge.rendered())
            return
