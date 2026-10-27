from dataclasses import dataclass, replace
from datetime import datetime
from typing import ClassVar

from journal.events.rows.memory_removed import MemoryRemoved
from journal.events.rows.memory_weighed import MemoryWeighed
from journal.models.scoped import Scoped
from journal.support.rejection import Rejection

LIGHTEST = 0
LOWEST_WEIGHT = 1
HEAVIEST = 10


@dataclass(frozen=True)
class Memory(Scoped):
    """What one agent keeps in mind in an environment, the main agent or a helper its owner by a link, with a weight from 0 to 10 that each of its owner's compactions lowers by one; at nought it is no longer shown, and a removed one stays on its row, never shown again."""

    text_fields: ClassVar[tuple[str, ...]] = ("text",)

    text: str = ""
    weight: int = 5
    keywords: tuple[str, ...] = ()
    removed_at: datetime | None = None

    def weighed(self, weight: int) -> "Memory":
        if not LOWEST_WEIGHT <= weight <= HEAVIEST:
            raise Rejection(f"a weight is a whole number from {LOWEST_WEIGHT} to {HEAVIEST}, not {weight}")
        return replace(self, weight=weight)

    def reweighed(self, weight: int) -> "Memory":
        return self.weighed(weight).with_event(MemoryWeighed(weight=weight))

    def faded(self) -> "Memory":
        return replace(self, weight=max(LIGHTEST, self.weight - 1))

    def removed(self, removal_time: datetime) -> "Memory":
        if self.removed_at is not None:
            raise Rejection(f"memory {self.id} is already removed")
        return replace(self, removed_at=removal_time).with_event(MemoryRemoved())

    def is_visible(self) -> bool:
        return self.weight > LIGHTEST and self.removed_at is None

    def summary_line(self) -> str:
        return self.opening_line(self.text)
