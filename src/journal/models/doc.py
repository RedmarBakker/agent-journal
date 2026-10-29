from dataclasses import dataclass, field
from typing import ClassVar

from journal.models.scoped import Scoped
from journal.models.support.abstract_text import ABSTRACT_LENGTH_CHARACTERS
from journal.models.support.abstracted import Abstracted
from journal.models.support.commentable import Commentable


@dataclass(frozen=True)
class Doc(Abstracted, Scoped, Commentable):
    """A document of one environment, read in every environment when it is the project's (environment 0): a title, a line that says what it is, its text, whether it is still being written in parts or ready, and why it needs no action once it is signed off as such."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "abstract", "body")

    title: str = ""
    abstract: str = field(default="", metadata={"characters": (1, ABSTRACT_LENGTH_CHARACTERS)})
    body: str = ""
    settled_reason: str = ""
    unfinished: bool = False

    def writing_status(self) -> str:
        return "Being written" if self.unfinished else "Ready"

    def finished(self) -> "Doc":
        return self.with_(unfinished=False)

    def summary_line(self) -> str:
        return self.abstract
