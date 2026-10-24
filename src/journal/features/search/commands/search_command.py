from argparse import Namespace

from journal.console.command import HELPER_KINDS, Command
from journal.support.caller import Caller
from journal.events.announcer import Announcer
from journal.events.moments.search_made import SearchMade
from journal.features.search.support.search import CONVERSATION, Search
from journal.repositories.scope import Scope


class SearchCommand(Command):
    """journal search "<words>" [--model message,plan]: every row here that holds all the words, in every model or the ones named, and a mark in the chat that opens what was found."""

    noun = "search"
    callers = {"find": HELPER_KINDS}
    default_verb = "find"

    def __init__(self, search: Search, announcer: Announcer, scope: Scope) -> None:
        self.search, self.announcer, self.scope = search, announcer, scope

    def arguments(self, verbs) -> None:
        search_verb = self.verb(verbs, "find", "find the rows and conversations here that hold every one of the words")
        search_verb.add_argument("terms", nargs="+")
        search_verb.add_argument("--model", default="", help=f"only these models, by name and comma apart: {', '.join(self.search.models())}; {CONVERSATION} reads the agents' conversations too")

    def find(self, args: Namespace, caller: Caller) -> int:
        terms = " ".join(args.terms).split()
        rows = self.search.kind_hits(terms, args.model.split(",")) if args.model else self.search.hits(terms)
        lines = [row.line() for row in rows]
        answer = "\n".join(lines) if lines else f"nothing here holds all of: {' '.join(terms)}"
        print(answer)
        self.announcer.announce(SearchMade(environment_id=self.scope.id, session=caller.session, terms=" ".join(terms), answer=answer))
        return 0
