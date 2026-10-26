from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReaderReportRaised(RowEvent):
    """The reader judge raised a report on how a reader read a run, for the session that ran it."""

    feature_name = "shell"

    session: str | None
