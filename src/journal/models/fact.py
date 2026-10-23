from dataclasses import dataclass, field
from typing import ClassVar

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class Fact(Scoped):
    text_fields: ClassVar[tuple[str, ...]] = ("text",)

    text: str = ""
    keywords: tuple[str, ...] = ()
    trigger: str = ""
    condition: dict = field(default_factory=dict)
    is_single_use: bool = False
    presence: bool = False

    def summary_line(self) -> str:
        return self.opening_line(self.text)
