from typing import ClassVar
from dataclasses import dataclass

from journal.models.model import Model

# the purpose of a template that says how a plan's agent tests its work
TESTING = "testing"


@dataclass(frozen=True)
class Template(Model):
    """Saved instructions and a starting outline for new items, written once and used many times, and for a plan's testing template the commands that run at each phase end. Project-wide."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "purpose", "brief")
    title: str = ""
    targets: tuple[str, ...] = ()
    purpose: str = ""
    brief: str = ""
    parts: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.opening_line(self.brief)
