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
            (worker, task_id)
            for worker, task_id, task_domain in self.waiting_for_check_in_plan(plan)
            if task_domain == domain
        )

    def tasks_waiting_for_check(self, plan: Plan) -> set[int]:
        return {task_id for _, task_id, _ in self.waiting_for_check_in_plan(plan)}

    def waiting_for_check_in_plan(self, plan: Plan) -> tuple[tuple[int, int, str], ...]:
        with self.scope.environment(plan.environment_id):
            waiting = []
            for worker in self.workers.global_matching(state=WorkerState.DELIVERED):
                if not worker.role:
                    continue
                for task_id in self.tasks.holder_task_ids(Ref.build(worker)):
                    domain = self.domain_for_task(worker, task_id, plan)
                    if domain and self.matches(worker, task_id, plan, domain):
                        waiting.append((worker.id, task_id, domain))
            return tuple(waiting)

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
