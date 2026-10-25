from argparse import Namespace

from journal.console.command import Command
from journal.support.caller import Caller
from journal.sync.session_leases import SessionLeases


class SessionCommand(Command):
    """journal session start <name>: a session on the team's hub, held by this machine alone while it holds the session's lease."""

    noun = "session"

    def __init__(self, sessions: SessionLeases) -> None:
        self.sessions = sessions

    def arguments(self, verbs) -> None:
        starting = self.verb(verbs, "start", "make a session on the team's hub, or take one up that no other machine holds; this machine is then its host")
        starting.add_argument("name")

    def start(self, args: Namespace, caller: Caller) -> int:
        session = self.sessions.start(args.name, caller.actor)
        print(f"session {session.team_name} is held by this machine, its host, on its branch {session.branch}")
        return 0
