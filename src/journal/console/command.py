from argparse import ArgumentParser, Namespace
from typing import ClassVar
from journal.console.support.chained_line import ChainedLine

from journal.support.caller import Caller


class Command:
    """One noun; each verb is a method named after it, taking the parsed arguments and where and by whom it runs. The main agent, the user and a plugin run every verb; a helper runs only the verbs its own file names. A verb runs in the agent's shell in the foreground, unless a feature's command names it among its background verbs, which go to the background at once with a card in the chat; and among its whole verbs, whose answer hands the agent its next step or a decision, a verb the agent may never cut with tail, head, grep or the like."""

    noun: ClassVar[str]
    default_verb: ClassVar[str] = ""
    background_verbs: ClassVar[frozenset[str]] = frozenset()
    uncut_verbs: ClassVar[frozenset[str]] = frozenset()
    def arguments(self, verbs) -> None:
        ...

    def perform(self, args: Namespace, caller: Caller) -> int:
        return (getattr(self, f"{args.verb}_", None) or getattr(self, args.verb))(args, caller)

    def chained(self, args: Namespace, caller: Caller) -> list[ChainedLine]:
        chain = getattr(self, f"{args.verb}_chain", None)
        return chain(args, caller) if chain else []

    @staticmethod
    def verb(verbs, name: str, help: str) -> ArgumentParser:
        parser = verbs.add_parser(name, help=help)
        parser.set_defaults(verb=name)
        return parser
