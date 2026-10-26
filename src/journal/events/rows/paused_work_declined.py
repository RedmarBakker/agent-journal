from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PausedWorkDeclined(RowEvent):
    """An agent set its paused work aside until its next close, by journal task skip-paused or by the user's own words while it was choosing."""

    feature_name = "tasks"

    agent_session: str
