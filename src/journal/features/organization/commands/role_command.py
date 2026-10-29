from argparse import Namespace

from journal.console.command import Command
from journal.engine.command_events import CommandEvents
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_queue import RoleQueue
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.tasks.active_task import ActiveTask
from journal.models.plan_mode import PlanMode
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class RoleCommand(Command):
    """journal role take <role> and journal role done: a solo Plan agent takes on one Role of the organization for its next step and ends it; a Role every plan shares is never taken on: the step's task waits in the queue of its one instance."""

    noun = "role"

    def __init__(
        self,
        events: CommandEvents,
        organization: Organization,
        plan_agents: PlanAgents,
        scope: Scope,
        queue: RoleQueue,
        tasks: Tasks,
        taking: ActiveTask,
        plans: Plans,
    ) -> None:
        self.events, self.organization, self.plan_agents, self.scope, self.plans = events, organization, plan_agents, scope, plans
        self.queue, self.tasks, self.taking = queue, tasks, taking

    def arguments(self, verbs) -> None:
        take = self.verb(verbs, "take", "act as a Role of the organization for your next step, by its id; a Role every plan shares takes the step's task in its queue instead")
        take.add_argument("role")
        take.add_argument("--task", type=int, default=0, help="the step's task, for a Role every plan shares; the task in your hands when not named")
        self.verb(verbs, "done", "the step you worked as a Role has ended")

    def take(self, args: Namespace, caller: Caller) -> int:
        plan = self.plan_agents.led_plan(self.scope.id)
        if plan is None or plan.mode != PlanMode.SOLO:
            raise Rejection("only the Plan agent of a solo plan takes on a Role, in its plan's environment")
        contracts = self.organization.contracts()
        role = contracts.role(args.role)
        if role is None:
            raise Rejection(f"no Role {args.role} in the organization; its Roles are {', '.join(known.id for known in contracts.roles) or 'none'}")
        if role.waits_in_queue():
            return self.queued(role, args, caller)
        task = self.plans.started_task(plan) or self.plans.following_task(plan)
        self.events.role_taken(role.id, task.row_id if task else 0, caller)
        print(f"you act as {role.title} for this step")
        return 0

    def queued(self, role: Role, args: Namespace, caller: Caller) -> int:
        holder = self.taking.holder(caller)
        task = self.tasks.find(args.task) if args.task else (self.tasks.holder_task(holder) if holder else None)
        if task is None:
            raise Rejection(f"{role.title} is shared by every plan, so its step waits in its queue: name the step's task with --task")
        instance = self.queue.queued(role, task, holder, caller.actor)
        print(f"task {task.id} waits in the queue of {role.title}, worker {instance.id} {instance.name}")
        return 0

    def done(self, args: Namespace, caller: Caller) -> int:
        self.events.role_step_ended(caller)
        print("the step as a Role has ended")
        return 0
