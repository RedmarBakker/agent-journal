from journal.support.alias_call import AliasCall
from journal.models.alias import Alias
from journal.repositories.aliases import Aliases
from journal.support.chain import Chain
from journal.support.command_shape import CommandShape


class AliasLines:
    """A shell line with each journal <alias> [args] part written out as the line its alias stands for, the alias an argv typed at a terminal calls, the alias a written-out part runs, the part of a line that calls an alias, and the part of a line that runs one moving to the background at once."""

    def __init__(self, aliases: Aliases, shapes: CommandShape) -> None:
        self.aliases, self.shapes = aliases, shapes

    def expanded(self, line: str) -> str:
        return Alias.resolved(line, self.aliases.index())

    def called(self, argv: list[str]) -> Alias | None:
        return self.aliases.index().get(argv[0]) if argv else None

    def running(self, part: str) -> Alias | None:
        return max((alias for alias in self.aliases.index().values() if self.matches(alias, part)), key=lambda alias: len(alias.line), default=None)

    def matches(self, alias: Alias, part: str) -> bool:
        shape = self.shapes.build(part)
        return alias.starts(part) or " " in shape and shape == self.shapes.build(alias.line)

    def line_alias(self, line: str) -> Alias | None:
        return next((alias for part in Chain.self_parts(line) if (alias := self.running(part)) is not None), None)

    def alias_part(self, line: str) -> str:
        return next((part for part in Chain.self_parts(line) if self.expanded(part) != part), "")

    def background_part(self, line: str) -> str:
        return next((part for part in Chain.self_parts(line) if (alias := self.running(part)) is not None and alias.background), "")
