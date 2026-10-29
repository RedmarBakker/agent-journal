from journal.features.organization.support.caps import Caps
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_queue_length import RoleQueueLength
from journal.features.organization.support.seat_runtime import SeatAddress, SeatRuntime
from journal.features.organization.support.usage_ledger import UsageEstimate, UsageLedger
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.time_source import TimeSource


class PlanTeam:
    """A plan's staffed Role seats, their current plan work and recorded per-seat estimates."""

    def __init__(self, plans: Plans, organization: Organization, staffing: RigStaffing, runtime: SeatRuntime,
                 workers: Workers, tasks: Tasks, queues: RoleQueueLength, usage: UsageLedger, caps: Caps,
                 time_source: TimeSource) -> None:
        self.plans, self.organization, self.staffing, self.runtime = plans, organization, staffing, runtime
        self.workers, self.tasks, self.queues, self.usage, self.caps = workers, tasks, queues, usage, caps
        self.time_source = time_source

    def build(self, plan: Plan) -> dict:
        if plan.mode != PlanMode.ORGANIZATION:
            estimate = self.usage.estimate(plan.id, self.time_source.seconds())
            return self.result([], estimate)

        rig_id = self.plans.rig_id(plan)
        rig = self.staffing.find_rig(rig_id) if rig_id else None
        tasks = self.plans.plan_tasks(plan)
        task_by_id = {task.row_id: task for task in tasks}
        contracts = self.organization.contracts()
        addresses = self.runtime.roster(rig.name) if rig else ()
        working, shared_working = self.working(plan, task_by_id, contracts)
        shared_waiting = self.waiting(tasks, task_by_id, contracts)
        estimates = self.usage.seat_estimates(plan.id)
        domains = self.domains(contracts, addresses, rig.name if rig else "", estimates, working, shared_working, shared_waiting)
        expected_seats = self.runtime.expected_seats(rig.name) if rig else None
        estimate = self.usage.estimate(plan.id, self.time_source.seconds(), expected_seats)
        return self.result(domains, estimate)

    def result(self, domains: list[dict], estimate: UsageEstimate) -> dict:
        return {
            "domains": domains,
            "seat_cap": int(self.caps.seats(0).limit),
            "estimated_api_cost_usd": estimate.amount_usd,
            "cost_cap_usd": self.caps.plan_cost(estimate).limit,
        }

    def working(self, plan: Plan, task_by_id: dict[int, Task], contracts: Contracts) -> tuple[dict[tuple[str, str], Task], list[tuple[Role, Task]]]:
        task_ids = set(task_by_id)
        seats: dict[tuple[str, str], Task] = {}
        shared = []
        for worker in self.workers.all_dispatched():
            role = contracts.role(worker.role) if worker.role else None
            if role is None:
                continue
            current = sorted(task_ids.intersection(self.tasks.holder_task_ids(Ref.build(worker))))
            if not current:
                continue
            task = task_by_id[current[0]]
            if role.cardinality is Cardinality.JOURNAL:
                shared.append((role, task))
            elif worker.plan_id == plan.id:
                member = f"{role.id}-{worker.id}" if role.cardinality is Cardinality.MANY else role.id
                seats[(role.domain, member)] = task
        return seats, shared

    def waiting(self, tasks: list[Task], task_by_id: dict[int, Task], contracts: Contracts) -> list[tuple[Role, Task]]:
        links = self.queues.queued_for(tasks)
        worker_ids = sorted({source.id for source, target in links if target.id in task_by_id and source.type == Worker.table()})
        workers = {worker.row_id: worker for worker in self.workers.selected_globally(self.workers.query().filter_listed("id", worker_ids))} if worker_ids else {}
        waiting = []
        for source, target in links:
            worker, task = workers.get(source.id), task_by_id.get(target.id)
            role = contracts.role(worker.role) if worker and worker.role else None
            if task and role and role.cardinality is Cardinality.JOURNAL:
                waiting.append((role, task))
        return waiting

    def domains(self, contracts: Contracts, addresses: tuple[SeatAddress, ...], rig: str, estimates: dict[str, float | None],
                working: dict[tuple[str, str], Task], shared_working: list[tuple[Role, Task]],
                shared_waiting: list[tuple[Role, Task]]) -> list[dict]:
        domains = {domain.id: domain for domain in contracts.domains}
        seats: dict[str, list[dict]] = {domain.id: [] for domain in contracts.domains}
        roles = {domain.id: contracts.roles_of(domain.id) for domain in contracts.domains}
        for address in addresses:
            domain = domains.get(address.pod)
            role = self.role_for_member(roles.get(address.pod, ()), address.member)
            if domain is None or role is None:
                continue
            task = working.get((domain.id, address.member))
            seats[domain.id].append(self.role_seat(
                address.member, role, task, estimates.get(self.runtime.target(rig, address.pod, address.member)) if rig else None
            ))
        for state, rows in (("working", shared_working), ("waiting", shared_waiting)):
            for role, task in rows:
                if role.domain in seats:
                    seats[role.domain].append(self.role_seat(f"shared:{role.id}:{task.id}", role, task, None, state, shared=True))
        return [
            {"id": domain.id, "title": domain.title, "seats": seats[domain.id]}
            for domain in contracts.domains if seats[domain.id]
        ]

    @staticmethod
    def role_for_member(roles: tuple[Role, ...], member: str) -> Role | None:
        for role in sorted(roles, key=lambda candidate: len(candidate.id), reverse=True):
            if role.cardinality is Cardinality.PLAN and member == role.id:
                return role
            prefix = f"{role.id}-"
            if role.cardinality is Cardinality.MANY and member.startswith(prefix) and member[len(prefix):].isdigit():
                return role
        return None

    @staticmethod
    def role_seat(member: str, role: Role, task: Task | None, estimate: float | None, state: str = "idle", shared: bool = False) -> dict:
        return {
            "id": member,
            "role_id": role.id,
            "title": role.title,
            "state": "working" if task and state == "idle" else state,
            "task_id": task.id if task else None,
            "task_title": task.title if task else "",
            "shared": shared,
            "estimated_api_cost_usd": estimate,
        }
