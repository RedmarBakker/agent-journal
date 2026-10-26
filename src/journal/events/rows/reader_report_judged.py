from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReaderReportJudged(RowEvent):
    """A verifier gave its verdict on a reader report's dismissal: sound, and the report stays closed, or not, and the report is open again; the verifier's session ends with it."""

    feature_name = "verification"

    verifier_session: str
    is_sound: bool
    reason: str
