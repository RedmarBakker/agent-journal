from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunAbandoned(RowEvent):
    """The agent gave its sequence up, its remaining steps undone."""

    feature_name = "sequences"

    agent_session: str
    reason: str
