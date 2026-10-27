from argparse import Namespace

from journal.support.caller import Caller

from journal.features.memory.commands.record_command import RecordCommand
from journal.features.memory.support.memory_context import MemoryContext
from journal.models.rule import Rule
from journal.repositories.rules import Rules


class RuleCommand(RecordCommand):
    """A rule binds the whole project, so it has no environment."""

    noun = "rule"

    def __init__(self, rules: Rules, context: MemoryContext) -> None:
        super().__init__(context)
        self.repository = rules

    def for_caller(self, row: Rule, caller: Caller) -> Rule:
        return row.created(caller.actor.is_agent())

    def new(self, args: Namespace) -> Rule:
        return Rule(text=args.text, reason=args.reason, keywords=self.keywords(args))
