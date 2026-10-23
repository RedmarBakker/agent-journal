from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class Reminder(Scoped):
    """What to keep doing in an environment, informed at every session start; a timed one stays quiet until its moment, is informed once then, and is struck."""

    text_fields: ClassVar[tuple[str, ...]] = ("text",)
    MOMENT: ClassVar[str] = "%Y-%m-%d %H:%M"

    text: str = ""
    keywords: tuple[str, ...] = ()
    trigger: str = ""
    condition: dict = field(default_factory=dict)
    is_single_use: bool = False
    presence: bool = False
    due_at: datetime | None = None

    def summary_line(self) -> str:
        return self.opening_line(self.text)
