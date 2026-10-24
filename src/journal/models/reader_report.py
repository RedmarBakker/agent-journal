from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class ReaderReport(Scoped):
    """What the reader judge found when a reader read a run poorly: the reader, the output and command it read, the session that ran it, what fell short with its evidence and the fix for each, when the agent read the report and, if it dismissed the report, why."""

    shared: ClassVar[bool] = False
    text_fields: ClassVar[tuple[str, ...]] = ("reader", "command")

    reader: str = ""
    output: int = 0
    command: str = ""
    session: str | None = None
    findings: tuple[str, ...] = ()
    fixes: tuple[str, ...] = ()
    read_at: datetime | None = None
    dismissal: str = ""

    def opened(self, time: datetime) -> "ReaderReport":
        return self if self.read_at else self.with_(read_at=time)

    def dismissed(self, reason: str) -> "ReaderReport":
        return self.with_(dismissal=reason)

    def full_text(self) -> str:
        finding_lines = "\n".join(f"- {finding}" for finding in self.findings)
        fix_lines = "\n".join(f"- {fix}" for fix in self.fixes)
        return f"reader report {self.id}: the reader {self.reader} on output {self.output} ({self.command})\n\nwhat fell short:\n{finding_lines}\n\nhow to fix it:\n{fix_lines}\n\nwrite the reader anew with journal reader add {self.reader} ..., or journal reader dismiss {self.id} --why \"<why the report is wrong>\""
