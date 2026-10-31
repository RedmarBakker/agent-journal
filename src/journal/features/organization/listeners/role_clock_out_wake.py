from journal.events.listener import Listener
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.role_work_checks import RoleWorkChecks
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.repositories.plans import Plans
from journal.models.plan_state import PlanState
from journal.repositories.workers import Workers


class RoleClockOutWake(Listener[WorkerDelivered]):
    """Wake the Domain seat that sent a Role worker when its work is ready to check."""

    def __init__(self, workers: Workers, plans: Plans, checks: RoleWorkChecks, runtime: SeatRuntime) -> None:
        self.workers, self.plans, self.checks, self.runtime = workers, plans, checks, runtime

    def handle(self, event: WorkerDelivered) -> None:
        if not event.task_id:
            return
        worker = self.workers.find(event.worker.id)
        if not worker.role:
            return
        plans = [plan for plan in self.plans.global_matching(state=PlanState.STARTED)
                 if self.plans.includes_task_or_part(plan.id, event.task_id)]
        for plan in plans:
            domain = self.checks.domain_for_task(worker, event.task_id, plan)
            if not domain or not self.checks.is_waiting_for_check(worker, event.task_id, plan, domain):
                continue
            rig = f"plan-{plan.id}"
            recipient = self.runtime.organization_member(rig, f"domain:{domain}", worker.provider)
            nudge = OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=worker.id, task=event.task_id)
            self.runtime.send(recipient, nudge.rendered())
            return
