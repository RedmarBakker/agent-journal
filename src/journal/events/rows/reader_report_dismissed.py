from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReaderReportDismissed(RowEvent):
    """An agent set a reader report aside as wrong, with its reason, which a verifier the journal sends then judges."""

    reason: str
