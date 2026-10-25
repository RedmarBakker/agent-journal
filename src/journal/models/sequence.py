from typing import ClassVar
from dataclasses import dataclass

from journal.models.model import Model
from journal.support.rejection import Rejection


@dataclass(frozen=True)
class Sequence(Model):
    """Steps the agent follows in order, one at a time. Project-wide, so every environment can run it. One shipped with the journal is locked: shown, never changed or deleted."""

    text_fields: ClassVar[tuple[str, ...]] = ("title",)
    title: str = ""
    steps: tuple[str, ...] = ()
    trigger_event: str = ""
    end_condition: tuple[str, ...] = ()
    locked: bool = False

    def title_words(self) -> str:
        return self.title

    def unlocked(self) -> "Sequence":
        if self.locked:
            raise Rejection(f"sequence {self.id}, {self.title}, ships with the journal and is locked: it cannot be changed or deleted")
        return self
