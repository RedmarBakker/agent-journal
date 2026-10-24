from argparse import Namespace

from journal.console.command import WORKER_KINDS, Command
from journal.support.caller import Caller
from journal.hooks.command_events import CommandEvents


class ImpasseCommand(Command):
    """journal stuck "<why>": the agent is stuck, so the journal says nothing until its next tool use or prompt."""

    noun = "stuck"
    callers = {"declare": WORKER_KINDS}
    default_verb = "declare"

    def __init__(self, events: CommandEvents) -> None:
        self.events = events

    def arguments(self, verbs) -> None:
        self.verb(verbs, "declare", "say why you are stuck").add_argument("why")

    def declare(self, args: Namespace, caller: Caller) -> int:
        self.events.help_needed(args.why, caller)
        print("stuck; your next tool use or prompt lifts it")
        return 0
