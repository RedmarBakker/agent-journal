from argparse import Namespace

from journal.chat.docking import Docking
from journal.console.support.row_comments import COMMENTS_VERB, RowComments
from journal.support.caller import Caller

DOCK_VERBS = ("dock", "undock")


class RowVerbs:
    """The verbs every row noun has beside its own: dock pins the row above the chat and undock takes it down; comments lists the comments under a row of a Commentable model."""

    def __init__(self, docking: Docking, comments: RowComments) -> None:
        self.docking, self.comments = docking, comments

    def build(self, noun: str) -> set[str]:
        verbs = set(DOCK_VERBS) if noun in self.docking.nouns() else set()
        if noun in self.comments.nouns():
            verbs.add(COMMENTS_VERB)
        return verbs

    def add(self, noun: str, verbs) -> None:
        helps = {"dock": f"pin the {noun} above the chat until the user opens or closes it", "undock": f"take the {noun} down from above the chat", COMMENTS_VERB: f"list the comments written under a {noun}, each with where its passage sits now"}
        for verb in sorted(self.build(noun)):
            parser = verbs.add_parser(verb, help=helps[verb])
            parser.add_argument("n", type=int)
            parser.set_defaults(verb=verb)

    def has(self, noun: str, verb: str) -> bool:
        return verb in self.build(noun)

    def perform(self, args: Namespace, caller: Caller) -> int:
        if args.verb == COMMENTS_VERB:
            return self.comments.listed(args.noun, args.n)
        message = getattr(self.docking, args.verb)(args.noun, args.n, caller.actor)
        print(f"{message.data['heading']} {'docked above the chat' if args.verb == 'dock' else 'undocked'}")
        return 0
