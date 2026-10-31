from journal.features.organization.support.hub_routes import HubRoutes
from journal.features.organization.support.seat_runtime import SeatMember, SeatRuntime
from journal.models.organization_handoff import OrganizationHandoff
from journal.models.plan import Plan
from journal.models.task import Task
from journal.repositories.domain_rows import DomainRows
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class OrganizationHub:
    """Routes tasks from one generated organization seat to a permitted seat through the journal inbox."""

    def __init__(self, routes: HubRoutes, runtime: SeatRuntime, handoffs: OrganizationHandoffs,
                 tasks: Tasks, domains: DomainRows, plans: Plans, scope: Scope) -> None:
        self.routes, self.runtime, self.handoffs = routes, runtime, handoffs
        self.tasks, self.domains, self.plans, self.scope = tasks, domains, plans, scope

    def handoff(self, task_id: int, target: str, caller: Caller) -> None:
        source = caller.organization_seat
        member = self.seat(caller)
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
        if domain := self.domain(target):
            self.domains.task_tied(task, domain, caller.actor)
        self.handoffs.handoff(task, plan, target, caller.actor)
        print(f"task {task.id} routed from {member.organization_seat} to {target}")

    def inbox(self, caller: Caller) -> None:
        seat = caller.organization_seat
        member = self.seat(caller)
        if member.rig.startswith("plan-"):
            plan = self.plan_for_rig(member.rig)
            with self.scope.environment(plan.environment_id):
                self.print_inbox(seat, self.handoffs.in_plan(self.handoffs.pending(seat), plan), caller.actor)
            return
        self.print_inbox(seat, self.handoffs.pending(seat), caller.actor)

    def print_inbox(self, seat: str, rows: tuple[tuple[OrganizationHandoff, Plan, Task], ...], actor: Actor) -> None:
        if not rows:
            print(f"no tasks handed to {seat}")
        for handoff, plan, task in rows:
            self.handoffs.read(handoff, actor)
            print(f"plan {plan.id} task {task.id}: {task.title}\n{task.brief}")

    def seat(self, caller: Caller) -> SeatMember:
        if not caller.organization_seat or not caller.organization_rig or not caller.actor_token:
            raise Rejection("organization handoff and inbox run only from a generated organization seat")
        member = self.runtime.organization_member(caller.organization_rig, caller.organization_seat, caller.provider or "")
        if (member.token != caller.actor_token or member.environment != caller.environment or member.provider != caller.provider
                or member.root != str(self.runtime.config.root)):
            raise Rejection("this journal command does not match its generated organization seat")
        return member

    def validate_task(self, source: str, task: Task, rig: str) -> Plan:
        if rig.startswith("plan-"):
            plan = self.plan_for_rig(rig)
            if task not in self.plans.plan_tasks(plan):
                raise Rejection(f"task {task.id} is not in plan {plan.id}")
            if source == "plan":
                return plan
            if domain := self.domain(source):
                if domain not in self.domains.domain_names(task):
                    raise Rejection(f"task {task.id} has not been handed to {domain}")
                return plan
        if rig.startswith("organization-") and source.startswith("role:"):
            domain = self.domain(source)
            if domain not in self.domains.domain_names(task):
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
