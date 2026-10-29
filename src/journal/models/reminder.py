from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from journal.models.scoped import Scoped
from journal.models.support.commentable import Commentable


@dataclass(frozen=True)
class Reminder(Scoped, Commentable):
    """What to keep doing in an environment, informed at every session start; a timed one stays quiet until its moment, is informed once then, and is struck; one with an interval is sent again every so many minutes or tool uses while it holds, from the moment and tool use it was last sent."""

    text_fields: ClassVar[tuple[str, ...]] = ("text",)
    MOMENT: ClassVar[str] = "%Y-%m-%d %H:%M"

    text: str = ""
    keywords: tuple[str, ...] = ()
    trigger: str = ""
    condition: dict = field(default_factory=dict)
    is_single_use: bool = False
    presence: bool = False
    due_at: datetime | None = None
    every_minutes: int = 0
    every_tool_uses: int = 0
    said_at: float = 0.0
    said_tool_use: int = 0

    def sent(self, time: float, tool_use: int) -> "Reminder":
        return self.with_(said_at=time, said_tool_use=tool_use)

    def summary_line(self) -> str:
        return self.opening_line(self.text)
