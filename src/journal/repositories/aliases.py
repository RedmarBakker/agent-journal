from journal.models.alias import Alias
from journal.repositories.repository import Repository


class Aliases(Repository[Alias]):
    """The project's aliases, one row each, the same for every environment."""

    model = Alias

    def index(self) -> dict[str, Alias]:
        return {alias.name: alias for alias in self.rows()}

    def names(self) -> frozenset[str]:
        return frozenset(self.index())

    def longest_alias(self, part: str) -> Alias | None:
        return max((alias for alias in self.rows() if alias.matches(part)), key=lambda alias: len(alias.line), default=None)

    def reader_rows(self, reader: str) -> list[Alias]:
        return self.selected(self.query().filter(reader=reader).order("id"))

    def plugin_aliases(self) -> list[Alias]:
        return self.selected(self.query().filter_unequal("plugin", "").order("id"))

    def plugin_rows(self, plugin: str) -> list[Alias]:
        return self.all_matching(plugin=plugin)
