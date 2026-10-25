from journal.support.alias_call import AliasCall
from journal.models.alias import Alias
from journal.repositories.aliases import Aliases
from journal.support.chain import Chain


class AliasLines:
    """A shell line with each journal <alias> [args] part written out as the line its alias stands for, the alias an argv typed at a terminal calls, the alias a written-out part runs, and the part of a line that runs one moving to the background at once."""

    def __init__(self, aliases: Aliases) -> None:
        self.aliases = aliases

    def expanded(self, line: str) -> str:
        return Alias.resolved(line, self.aliases.index())

    def called(self, argv: list[str]) -> Alias | None:
        return self.aliases.index().get(argv[0]) if argv else None

    def running(self, part: str) -> Alias | None:
        return self.aliases.longest_alias(part)

    def line_alias(self, line: str) -> Alias | None:
        return next((alias for part in Chain.self_parts(line) if (alias := self.running(part)) is not None), None)

    def background_part(self, line: str) -> str:
        return next((part for part in Chain.self_parts(line) if (alias := self.running(part)) is not None and alias.background), "")
