from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunPaused(RowEvent):
    """The agent set its sequence aside, saying why."""

    feature_name = "sequences"

    agent_session: str
    reason: str
