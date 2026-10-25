from dataclasses import dataclass
from typing import ClassVar

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class Doc(Scoped):
    """A document of one environment, read in every environment when it is the project's (environment 0) or a hub's: a title, a line that says what it is, and its text."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "abstract", "body")

    title: str = ""
    abstract: str = ""
    body: str = ""

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.abstract or self.opening_line(self.body)
