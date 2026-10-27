from dataclasses import dataclass
from typing import ClassVar

from journal.models.model import Model


@dataclass(frozen=True)
class ReaderSuggestion(Model):
    """A part of a command line the journal suggested a reader for, in any environment of the project, and when; a reader added that reads the part takes it away."""

    shared: ClassVar[bool] = False

    part: str = ""
    suggested_at: float = 0.0
