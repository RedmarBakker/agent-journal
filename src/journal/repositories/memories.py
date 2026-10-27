from journal.db.query import Query
from journal.models.memory import LIGHTEST, Memory
from journal.repositories.repository import MATCH_ROWS, PAGE_ROWS
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor


class Memories(ScopedRepository[Memory]):
    """The environment's memories: those still shown, heaviest first, and the fading of every one by one at a compaction."""

    model = Memory

    def shown(self) -> list[Memory]:
        return self.selected(self.shown_query().order_descending("weight").limit(PAGE_ROWS))

    def fade_all(self, actor: Actor) -> list[Memory]:
        return [self.save(memory.faded(), actor) for memory in self.selected(self.shown_query())]

    def search(self, terms: list[str], limit: int = MATCH_ROWS) -> list[Memory]:
        return self.search_rows(self.query().filter_null("removed_at"), terms, limit)

    def shown_query(self) -> Query:
        return self.query().filter_greater("weight", LIGHTEST).filter_null("removed_at")
