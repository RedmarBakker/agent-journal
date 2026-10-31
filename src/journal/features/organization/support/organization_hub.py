from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.hub_routes import HubRoutes
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.seat_runtime import SeatMember, SeatRuntime
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_work_checks import RoleWorkChecks
from journal.features.organization.support.task_parts import TaskParts
from journal.features.workers.commands.worker_command import WorkerCommand
from journal.features.workers.support.owned_task_line import owned_task_line
from journal.models.organization_handoff import OrganizationHandoff
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.caller import Caller
from journal.support.missing_row import MissingRow
from journal.support.rejection import Rejection


class OrganizationHub:
    """Routes tasks from one generated organization seat to a permitted seat through the journal inbox."""

    def __init__(self, routes: HubRoutes, runtime: SeatRuntime, handoffs: OrganizationHandoffs,
                 tasks: Tasks, domains: DomainRows, plans: Plans, scope: Scope,
                 organization: Organization, workers: WorkerCommand, staffing: RigStaffing,
                 task_parts: TaskParts, role_work_checks: RoleWorkChecks) -> None:
        self.routes, self.runtime, self.handoffs = routes, runtime, handoffs
        self.tasks, self.domains, self.plans, self.scope = tasks, domains, plans, scope
        self.organization, self.workers, self.staffing = organization, workers, staffing
        self.task_parts = task_parts
        self.role_work_checks = role_work_checks

    def handoff(self, task_id: int, target: str, caller: Caller) -> None:
        source = caller.organization_seat
        member = self.seat(caller)
        if source.startswith("role:") and caller.worker_number is not None:
            raise Rejection(OrganizationNudges.ROLE_TASK_RETURN.rendered())
        refusal = self.routes.refusal_for(source, target)
        if refusal:
            raise Rejection(refusal)
        if member.rig.startswith("plan-"):
            plan = self.plan_for_rig(member.rig)
            with self.scope.environment(plan.environment_id):
                self.handoff_task(task_id, target, source, member, caller)
            return
        self.handoff_task(task_id, target, source, member, caller)

    def handoff_task(self, task_id: int, target: str, source: str, member: SeatMember, caller: Caller) -> None:
        task = self.tasks.find(task_id)
        plan = self.validate_task(source, task, member.rig)
        role = self.role(target)
        if role and self.tasks.parts_of(task):
            raise Rejection(OrganizationNudges.SPLIT_HANDOFF_REQUIRED.create(task=task.id).rendered())
        if role:
            self.tasks.require_assignment_ready(task)
            if role.writes:
                self.workers.require_role_task_dispatchable(task, role, caller)
        if domain := self.domain(target):
            if target.startswith("domain:"):
                if source == "plan" and self.plans.rig_id(plan):
                    self.staffing.place_domain(plan, domain, member.provider, member.environment)
                recipient = self.runtime.organization_member(self.target_rig(target, plan, role, member), target, member.provider)
                self.domains.task_tied(task, domain, caller.actor)
                self.handoffs.handoff(task, plan, target, caller.actor)
                self.runtime.send(recipient, OrganizationSeatRouting.handoff_prompt)
                print(f"task {task.id} routed from {member.organization_seat} to {target}")
                return
            self.domains.task_tied(task, domain, caller.actor)
        self.handoffs.handoff(task, plan, target, caller.actor)
        if role and role.writes:
            self.workers.dispatch_role_task(task, role, caller)
        elif target != "main":
            self.wake(target, plan, role, member)
        print(f"task {task.id} routed from {member.organization_seat} to {target}")

    def part(self, parent_id: int, target: str, title: str, brief: str, after: int, caller: Caller) -> None:
        source, member = caller.organization_seat, self.seat(caller)
        parent = self.task(parent_id)
        with self.scope.environment(parent.environment_id):
            self.create_part(parent, target, title, brief, after, source, member, caller)

    def create_part(self, parent: Task, target: str, title: str, brief: str, after: int,
                    source: str, member: SeatMember, caller: Caller) -> None:
        if not source.startswith("domain:") or caller.worker_number is not None:
            raise Rejection(OrganizationNudges.ROLE_TASK_RETURN.rendered())
        role = self.role(target)
        domain = source.removeprefix("domain:")
        if role is None:
            raise Rejection(f"{target} is not a Role in the organization contract")
        if role.domain != domain:
            raise Rejection(OrganizationNudges.SPLIT_OTHER_DOMAIN.create(domain=domain).rendered())
        if not role.writes:
            raise Rejection(f"role:{role.domain}/{role.id} does not write; give it a read-only assignment another way")
        refusal = self.routes.refusal_for(source, target)
        if refusal:
            raise Rejection(refusal)
        plan = self.validate_task(source, parent, member.rig)
        part = self.task_parts.part(parent, plan, domain, title, brief, after, caller.actor)
        self.handoffs.handoff(part, plan, target, caller.actor)
        if part.state == TaskState.BLOCKED:
            print(f"task {part.id} part of task {parent.id} waits for task {after} before {target}")
            return
        self.workers.dispatch_role_task(part, role, caller)
        print(f"task {part.id} part of task {parent.id} routed to {target}")

    def other(self, parent_id: int, target: str, title: str, brief: str, caller: Caller) -> None:
        source, member = caller.organization_seat, self.seat(caller)
        parent = self.task(parent_id)
        with self.scope.environment(parent.environment_id):
            self.create_other(parent, target, title, brief, source, member, caller)

    def create_other(self, parent: Task, target: str, title: str, brief: str,
                     source: str, member: SeatMember, caller: Caller) -> None:
        if not source.startswith("domain:") or caller.worker_number is not None:
            raise Rejection(OrganizationNudges.ROLE_TASK_RETURN.rendered())
        domain = self.domain(target)
        source_domain = source.removeprefix("domain:")
        if not domain or domain == source_domain:
            raise Rejection(f"organization other needs another Domain, not {target}")
        if self.organization.contracts().domain(domain) is None:
            raise Rejection(f"domain {domain} is not in the organization contract")
        plan = self.validate_task(source, parent, member.rig)
        task = self.task_parts.other(parent, plan, domain, title, brief, caller.actor)
        self.wake("plan", plan, None, member)
        print(f"task {task.id} added to plan {plan.id} as another Domain's part of task {parent.id}")

    def parts(self, parent_id: int, caller: Caller) -> None:
        self.seat(caller)
        parent = self.task(parent_id)
        with self.scope.environment(parent.environment_id):
            plans = self.plans.containing(parent)
            if len(plans) != 1:
                raise Rejection(f"task {parent.id} does not identify one plan for its parts")
            plan = plans[0]
            parts = self.tasks.parts_of(parent)
            if not parts:
                print(f"task {parent.id} has no parts")
                return
            workers_waiting = {
                task_id: worker for worker, task_id, _ in self.role_work_checks.waiting_for_check_in_plan(plan)
            }
            for part in parts:
                target = self.handoffs.latest_target(part, plan)
                waiting = ", ".join(f"task {ref.id}" for ref in self.tasks.open_waits(part))
                line = f"task {part.id} {part.state.value}, {target or 'not assigned'}"
                if worker := workers_waiting.get(part.id):
                    line = f"{line}, waits for check from worker {worker}"
                print(f"{line}, waits for {waiting}" if waiting else line)

    def task(self, task_id: int) -> Task:
        task = next(iter(self.tasks.global_matching(id=task_id)), None)
        if task is None:
            raise MissingRow(Task.table(), task_id)
        return task

    def split_progress(self, task: Task) -> str:
        with self.scope.environment(task.environment_id):
            parts = self.tasks.parts_of(task)
            if not parts:
                return ""
            completed = sum(part.state == TaskState.COMPLETED for part in parts)
            noun = "part" if len(parts) == 1 else "parts"
            return f", split into {len(parts)} {noun} with its Domain, {completed} merged"

    def wake(self, target: str, plan: Plan, role: Role | None, source: SeatMember) -> None:
        rig = self.target_rig(target, plan, role, source)
        recipient = self.runtime.organization_member(rig, target, source.provider)
        self.runtime.send(recipient, OrganizationSeatRouting.handoff_prompt)

    @staticmethod
    def target_rig(target: str, plan: Plan, role: Role | None, source: SeatMember) -> str:
        if target == "plan":
            return f"plan-{plan.id}"
        if target.startswith("domain:"):
            return source.rig if source.rig.startswith("organization-") else f"plan-{plan.id}"
        if role and role.cardinality is Cardinality.JOURNAL:
            return RigStaffing.shared_rig_name(plan.environment_id)
        return f"plan-{plan.id}"

    def inbox(self, caller: Caller) -> None:
        seat = caller.organization_seat
        member = self.seat(caller)
        if member.rig.startswith("plan-"):
            plan = self.plan_for_rig(member.rig)
            with self.scope.environment(plan.environment_id):
                self.print_inbox(seat, self.handoffs.in_plan(self.handoffs_for_inbox(seat), plan), caller)
            return
        self.print_inbox(seat, self.handoffs_for_inbox(seat), caller)

    def handoffs_for_inbox(self, seat: str) -> tuple[tuple[OrganizationHandoff, Plan, Task], ...]:
        return self.handoffs.awaiting_action(seat) if seat.startswith("domain:") else self.handoffs.pending(seat)

    def print_inbox(self, seat: str, rows: tuple[tuple[OrganizationHandoff, Plan, Task], ...], caller: Caller) -> None:
        if not rows:
            print(f"no tasks handed to {seat}")
        for handoff, plan, task in rows:
            self.handoffs.read(handoff, caller.actor)
            holder = self.tasks.holder(task)
            assignment = self.assignment(holder, task, caller)
            print(f"plan {plan.id} task {task.id}: {task.title}{assignment}\n{task.brief}")
            if seat.startswith("domain:"):
                for part in self.tasks.parts_of(task):
                    if part.state.is_closed():
                        continue
                    target = self.handoffs.latest_target(part, plan)
                    holder = self.tasks.holder(part)
                    assignment = self.assignment(holder, part, caller)
                    print(f"plan {plan.id} task {part.id}: {part.title} (part of task {task.id}, {target or 'not assigned'}){assignment}")

    @staticmethod
    def assignment(holder: Ref | None, task: Task, caller: Caller) -> str:
        if holder is None or holder.type != Worker.table():
            return ""
        if caller.worker_number == holder.id:
            return f"\n{owned_task_line(holder.id, task.id)}"
        return f"\nworker {holder.id} holds this task"

    def seat(self, caller: Caller) -> SeatMember:
        return self.runtime.member_for_caller(caller)

    def validate_task(self, source: str, task: Task, rig: str) -> Plan:
        if rig.startswith("plan-"):
            plan = self.plan_for_rig(rig)
            parent = self.tasks.part_of_task(task)
            plan_tasks = self.plans.plan_tasks(plan)
            if task not in plan_tasks and parent not in plan_tasks:
                raise Rejection(f"task {task.id} is not in plan {plan.id}")
            if source == "plan":
                if parent and task not in plan_tasks:
                    raise Rejection(f"task {task.id} is a Role part; the Plan seat receives parts but does not hand them on")
                return plan
            if domain := self.domain(source):
                if domain not in self.domains.domain_names(task) and domain not in self.domains.domain_names(parent or task):
                    raise Rejection(f"task {task.id} has not been handed to {domain}")
                return plan
        if rig.startswith("organization-") and source.startswith("role:"):
            domain = self.domain(source)
            parent = self.tasks.part_of_task(task)
            if domain not in self.domains.domain_names(task) and domain not in self.domains.domain_names(parent or task):
                raise Rejection(f"task {task.id} has not been handed to {domain}")
            plans = self.plans.containing(task)
            if len(plans) == 1:
                return plans[0]
            numbers = ", ".join(str(plan.id) for plan in plans) or "none"
            raise Rejection(f"task {task.id} does not identify one plan for its Domain handoff: {numbers}")
        raise Rejection(f"{source} cannot hand off task {task.id} from rig {rig}")

    def plan_for_rig(self, rig: str) -> Plan:
        prefix = "plan-"
        if not rig.startswith(prefix) or not rig.removeprefix(prefix).isdigit():
            raise Rejection(f"organization Plan seat is not in a plan rig: {rig}")
        matches = self.plans.global_matching(id=int(rig.removeprefix(prefix)))
        if not matches:
            raise Rejection(f"organization Plan seat has no plan {rig.removeprefix(prefix)}")
        return matches[0]

    @staticmethod
    def domain(identity: str) -> str:
        if identity.startswith("domain:"):
            return identity.removeprefix("domain:")
        if identity.startswith("role:"):
            return identity.removeprefix("role:").split("/", 1)[0]
        return ""

    def role(self, identity: str) -> Role | None:
        if not identity.startswith("role:"):
            return None
        domain, separator, role_id = identity.removeprefix("role:").partition("/")
        if not separator:
            return None
        return next((role for role in self.organization.contracts().roles
                     if role.domain == domain and role.id == role_id), None)
