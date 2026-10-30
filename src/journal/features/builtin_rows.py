from dataclasses import dataclass

from journal.models.model import Model
from journal.support.actor import Actor


@dataclass(frozen=True)
class BuiltinRows:
    """The rows of one kind that come with the journal, as a start finds them, by title: the row that stands for each title the journal brings, one the journal made itself before one the user never changed, and the leftovers to take away, rows the journal made and brings no more and older copies of a builtin one the user never changed; a row the user made and changed is never taken away."""

    stored: tuple[Model, ...]
    titles: frozenset[str]

    def standing(self, title: str) -> Model | None:
        titled = self.titled(title)
        return next((row for row in titled if self.is_builtin(row)), None) or next((row for row in titled if self.is_unchanged_copy(row)), None)

    def leftovers(self) -> list[Model]:
        retired = [row for row in self.stored if self.is_builtin(row) and row.title not in self.titles]
        copies = [row for title in self.titles for row in self.titled(title) if row is not self.standing(title) and self.is_unchanged_copy(row)]
        return [*retired, *copies]

    def titled(self, title: str) -> list[Model]:
        return [row for row in self.stored if row.title == title]

    @staticmethod
    def is_builtin(row: Model) -> bool:
        return row.creation_actor == Actor.system()

    @staticmethod
    def is_unchanged_copy(row: Model) -> bool:
        return not BuiltinRows.is_builtin(row) and row.creation_time == row.update_time
