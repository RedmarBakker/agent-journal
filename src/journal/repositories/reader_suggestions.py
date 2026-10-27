from journal.models.reader_suggestion import ReaderSuggestion
from journal.repositories.repository import Repository
from journal.support.actor import Actor


class ReaderSuggestions(Repository[ReaderSuggestion]):
    """The parts the journal suggested a reader for, the same for every environment of the project."""

    model = ReaderSuggestion

    def suggestion_times(self) -> dict[str, float]:
        return {row.part: row.suggested_at for row in self.all()}

    def suggested(self, part: str, time: float, actor: Actor) -> ReaderSuggestion:
        rows = self.matching(part=part)
        return self.save(rows[0].with_(suggested_at=time) if rows else ReaderSuggestion(part=part, suggested_at=time), actor)

    def cleared(self, parts: list[str], actor: Actor) -> None:
        for row in self.selected(self.query().filter_listed("part", parts)):
            self.delete(row, actor)
