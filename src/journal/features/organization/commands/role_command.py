from argparse import Namespace

from journal.console.command import Command
from journal.engine.command_events import CommandEvents
from journal.features.organization.support.organization import Organization
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.plan_mode import PlanMode
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class RoleCommand(Command):
    """journal role take <role> and journal role done: a solo Plan agent takes on one Role of the organization for its next step and ends it; a Role the whole journal shares is never taken on, its work waits on its queue."""

    noun = "role"

    def __init__(self, events: CommandEvents, organization: Organization, plan_agents: PlanAgents, scope: Scope) -> None:
        self.events, self.organization, self.plan_agents, self.scope = events, organization, plan_agents, scope

    def arguments(self, verbs) -> None:
        self.verb(verbs, "take", "act as a Role of the organization for your next step, by its id").add_argument("role")
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
            raise Rejection(f"{role.title} is shared by every plan, so no plan takes it on: its work waits on its queue")
        self.events.role_taken(role.id, caller)
        print(f"you act as {role.title} for this step")
        return 0

    def done(self, args: Namespace, caller: Caller) -> int:
        self.events.role_step_ended(caller)
        print("the step as a Role has ended")
        return 0
