from argparse import Namespace

from journal.console.command import Command
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.environment import Environment
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.sync.hub_drives import HubDrives
from journal.sync.session_leases import SessionLeases


class SessionCommand(Command):
    """journal session start <name>: a session on the team's hub, held by this machine alone while it holds the session's lease; with --plan it drives that hub plan too, taking the plan's lease as well, so a local environment and a session never drive one plan at once."""

    noun = "session"

    def __init__(self, sessions: SessionLeases, drives: HubDrives, bindings: PlanBindings, plans: Plans, environments: Environments, scope: Scope) -> None:
        self.sessions, self.drives, self.bindings, self.plans, self.environments, self.scope = sessions, drives, bindings, plans, environments, scope

    def arguments(self, verbs) -> None:
        starting = self.verb(verbs, "start", "make a session on the team's hub, or take one up that no other machine holds; this machine is then its host")
        starting.add_argument("name")
        starting.add_argument("--plan", type=int, default=0, help="a hub plan the session drives, refused while a local environment or another machine drives it")

    def start(self, args: Namespace, caller: Caller) -> int:
        if args.plan:
            return self.driving(args, caller)
        print(self.held_line(self.sessions.start(args.name, caller.actor)))
        return 0

    def driving(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.plan)
        self.bindings.check(plan, next((session.row_id for session in self.environments.session_rows([args.name])), 0))
        session = self.sessions.start(args.name, caller.actor)
        with self.scope.environment(session.row_id):
            driven = self.drives.drive(plan, caller.actor)
        print(f"{self.held_line(session)}\n{self.drives.drive_line(driven)}")
        return 0

    @staticmethod
    def held_line(session: Environment) -> str:
        return f"session {session.team_name} is held by this machine, its host, on its branch {session.branch}"
