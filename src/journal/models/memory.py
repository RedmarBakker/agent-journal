from dataclasses import dataclass, replace
from datetime import datetime
from typing import ClassVar

from journal.models.scoped import Scoped
from journal.support.rejection import Rejection

LIGHTEST = 0
HEAVIEST = 10


@dataclass(frozen=True)
class Memory(Scoped):
    """What the agent keeps in mind in an environment, with a weight from 0 to 10 that every compaction lowers by one; at nought it is no longer shown, and a removed one stays on its row, never shown again."""

    text_fields: ClassVar[tuple[str, ...]] = ("text",)

    text: str = ""
    weight: int = 5
    keywords: tuple[str, ...] = ()
    removed_at: datetime | None = None

    def weighed(self, weight: int) -> "Memory":
        if not LIGHTEST <= weight <= HEAVIEST:
            raise Rejection(f"a memory weighs {LIGHTEST} to {HEAVIEST}, not {weight}")
        return replace(self, weight=weight)

    def faded(self) -> "Memory":
        return replace(self, weight=max(LIGHTEST, self.weight - 1))

    def removed(self, at: datetime) -> "Memory":
        if self.removed_at is not None:
            raise Rejection(f"memory {self.id} is already removed")
        return replace(self, removed_at=at)

    def is_shown(self) -> bool:
        return self.weight > LIGHTEST and self.removed_at is None

    def summary_line(self) -> str:
        return self.opening_line(self.text)
