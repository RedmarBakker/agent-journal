from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class OverviewRead(RowEvent):
    """The agent read what is in progress here: the overview due at a start is done."""

    feature_name = "briefing"

