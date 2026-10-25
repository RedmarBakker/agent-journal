from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class EnvironmentUnshared(RowEvent):
    """An environment its owner shared with the team was taken back, so its rows leave the team."""
