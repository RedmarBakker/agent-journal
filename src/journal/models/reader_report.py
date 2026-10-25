from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from journal.events.rows.reader_report_dismissed import ReaderReportDismissed
from journal.events.rows.reader_report_judged import ReaderReportJudged
from journal.events.rows.reader_report_raised import ReaderReportRaised
from journal.models.scoped import Scoped
from journal.support.rejection import Rejection


CLEARED_VERDICT = "cleared by a later run that printed its total"


@dataclass(frozen=True)
class ReaderReport(Scoped):
    """What the reader judge found when a reader read a run poorly: the reader, the output and command it read, the session that ran it, what fell short with its evidence and the fix for each, when the agent read the report and, if it dismissed the report, why; and the verdict of the verifier the journal sent on that dismissal, its reason and when it was given, a refuted report open again until its reader is written anew."""

    shared: ClassVar[bool] = False
    text_fields: ClassVar[tuple[str, ...]] = ("reader", "command")

    reader: str = ""
    output: int = 0
    command: str = ""
    session: str | None = None
    findings: tuple[str, ...] = ()
    fixes: tuple[str, ...] = ()
    read_at: datetime | None = None
    dismissal: str | None = None
    is_refuted: bool = False
    verdict: str = ""
    judged_at: datetime | None = None

    def creation_events(self) -> tuple[ReaderReportRaised, ...]:
        return (ReaderReportRaised(environment_id=self.environment_id, session=self.session),)

    def opened(self, time: datetime) -> "ReaderReport":
        return self if self.read_at else self.with_(read_at=time)

    def dismissed(self, reason: str) -> "ReaderReport":
        if self.is_refuted:
            raise Rejection(f"reader report {self.id} was dismissed once and the dismissal was found wrong: {self.verdict}; it is met only by writing the reader {self.reader} anew with journal reader add {self.reader} ...")
        return self.with_(dismissal=reason).with_event(ReaderReportDismissed(environment_id=self.environment_id, reason=reason))

    def cleared(self, time: datetime) -> "ReaderReport":
        return self.with_(dismissal=CLEARED_VERDICT, verdict=CLEARED_VERDICT, judged_at=time)

    def judged_sound(self, reason: str, verifier_session: str, time: datetime) -> "ReaderReport":
        return self.judged(reason, time).with_event(self.judgement(verifier_session, True, reason, time))

    def refuted(self, reason: str, verifier_session: str, time: datetime) -> "ReaderReport":
        return self.judged(reason, time).with_(dismissal=None, is_refuted=True).with_event(self.judgement(verifier_session, False, reason, time))

    def judged(self, reason: str, time: datetime) -> "ReaderReport":
        if self.judged_at is not None or self.dismissal is None:
            raise Rejection(f"reader report {self.id} has no dismissal waiting for a verdict")
        return self.with_(verdict=reason, judged_at=time)

    def judgement(self, verifier_session: str, is_sound: bool, reason: str, time: datetime) -> ReaderReportJudged:
        return ReaderReportJudged(environment_id=self.environment_id, time=time.timestamp(), verifier_session=verifier_session, is_sound=is_sound, reason=reason)

    def evidence(self) -> str:
        finding_lines = "\n".join(f"- {finding}" for finding in self.findings)
        fix_lines = "\n".join(f"- {fix}" for fix in self.fixes)
        return f"reader report {self.id}: the reader {self.reader} on output {self.output} ({self.command})\n\nwhat fell short:\n{finding_lines}\n\nhow to fix it:\n{fix_lines}"

    def full_text(self) -> str:
        return f"{self.evidence()}\n\nwrite the reader anew with journal reader add {self.reader} ..., or journal reader dismiss {self.id} --why \"<why the report is wrong>\""
