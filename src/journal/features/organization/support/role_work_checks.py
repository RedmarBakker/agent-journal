from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers


class RoleWorkChecks:
    """Find Role work that a Domain seat still needs to check."""

    def __init__(self, workers: Workers, tasks: Tasks, domains: DomainRows, handoffs: OrganizationHandoffs,
                 plans: Plans, scope: Scope) -> None:
        self.workers, self.tasks, self.domains = workers, tasks, domains
        self.handoffs, self.plans, self.scope = handoffs, plans, scope

    def waiting_for_check(self, plan: Plan, domain: str) -> tuple[tuple[int, int], ...]:
        if not domain:
            return ()
        return tuple(
            (worker.id, task_id)
            for worker in self.workers.global_matching(state=WorkerState.DELIVERED)
            if worker.role
            for task_id in self.tasks.holder_task_ids(Ref.build(worker))
            if self.matches(worker, task_id, plan, domain)
        )

    def is_waiting_for_check(self, worker: Worker, task_id: int, plan: Plan, domain: str) -> bool:
        with self.scope.environment(plan.environment_id):
            return self.matches(worker, task_id, plan, domain)

    def matches(self, worker: Worker, task_id: int, plan: Plan, domain: str) -> bool:
        if (plan.mode != PlanMode.ORGANIZATION or worker.state != WorkerState.DELIVERED
                or not worker.role):
            return False
        if task_id not in self.tasks.holder_task_ids(Ref.build(worker)):
            return False
        if not self.plans.includes_task_or_part(plan.id, task_id):
            return False
        tasks = self.tasks.global_matching(id=task_id)
        if not tasks:
            return False
        with self.scope.environment(plan.environment_id):
            task = tasks[0]
            return domain in self.domains.domain_names(task) and self.handoffs.latest_target(task, plan) == f"role:{domain}/{worker.role}"

    def domain_for_task(self, worker: Worker, task_id: int, plan: Plan) -> str:
        tasks = self.tasks.global_matching(id=task_id)
        if not tasks:
            return ""
        with self.scope.environment(plan.environment_id):
            target = self.handoffs.latest_target(tasks[0], plan)
        prefix, separator, role = target.removeprefix("role:").partition("/")
        return prefix if target.startswith("role:") and separator and role == worker.role else ""
