from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Self

from journal.models.scoped import Scoped
from journal.models.support.abstract_text import ABSTRACT_LENGTH_CHARACTERS, AbstractText
from journal.models.support.dock_button import DockButton
from journal.models.support.dock_card import DockCard
from journal.support.rejection import Rejection

UPDATE = "update"
SECTION_NAMES = {"need": ("waits on you", "wait on you"), "done": ("done", "done"), "doing": ("under way", "under way"), "plans": ("plan under way", "plans under way"), "commits": ("commit", "commits"), "also": ("also written", "also written")}


@dataclass(frozen=True)
class Report(Scoped):
    """What was checked or researched now; an update report is of kind update, its abstract the agent's summary and its items the rows the journal gathered for the time it covers, each with its section, ref, title and note, the moment the user read it, and why it needs no action once it is signed off as such."""

    column_renames: ClassVar[dict[str, str]] = {"kind": "report_type"}

    text_fields: ClassVar[tuple[str, ...]] = ("title", "abstract", "body")

    title: str = ""
    abstract: str = field(default="", metadata={"characters": (1, ABSTRACT_LENGTH_CHARACTERS)})
    body: str = ""
    report_type: str = ""
    items: tuple = ()
    start_at: datetime | None = None
    end_at: datetime | None = None
    read_at: datetime | None = None
    settled_reason: str = ""
    unfinished: bool = False

    def title_words(self) -> str:
        return self.title

    def refusal(self) -> str:
        return AbstractText.refusal(self.abstract)

    def pulled_row(self) -> Self:
        return self.with_(abstract=AbstractText.fitted(self.abstract, self.body, self.title))

    @classmethod
    def pulled_fields(cls, fields: dict) -> dict:
        return {name: value for name, value in fields.items() if name != "abstract" or not AbstractText.refusal(value)}

    def summary_line(self) -> str:
        if self.is_update():
            return f"{self.abstract} ({self.counts_text()})" if self.items else self.abstract
        return self.abstract

    def counts_text(self) -> str:
        counts = {section: sum(1 for item in self.items if item["section"] == section) for section in SECTION_NAMES}
        return ", ".join(f"{count} {SECTION_NAMES[section][count != 1]}" for section, count in counts.items() if count)

    def docked(self) -> DockCard:
        return DockCard((DockButton("Open update", "open_update"), DockButton("Close", "close"))) if self.is_update() else DockCard.plain()

    def is_update(self) -> bool:
        return self.report_type == UPDATE

    def writing_status(self) -> str:
        return "Being written" if self.unfinished else "Ready"

    def finished(self) -> "Report":
        return self.with_(unfinished=False)

    def read(self, time: datetime) -> "Report":
        return self if self.read_at else self.with_(read_at=time)

    def item_added(self, section: str, ref: str, title: str) -> "Report":
        return self.with_(items=(*self.items, {"section": section, "ref": ref, "title": title}))

    def noted(self, n: int, note: str) -> "Report":
        self.numbered_item(n)
        return self.with_(items=tuple({**item, "note": note} if index == n else item for index, item in enumerate(self.items, start=1)))

    def dropped(self, n: int) -> "Report":
        self.numbered_item(n)
        return self.with_(items=tuple(item for index, item in enumerate(self.items, start=1) if index != n))

    def numbered_item(self, n: int) -> dict:
        if not 1 <= n <= len(self.items):
            raise Rejection(f"update {self.id} has {len(self.items)} items: journal report show {self.id} lists them")
        return self.items[n - 1]
