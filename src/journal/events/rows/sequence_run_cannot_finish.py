from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunCannotFinish(RowEvent):
    """A sequence an agent runs cannot finish, since what it was about is gone."""

    feature_name = "sequences"

    agent_session: str
    sequence_id: int
    reason: str
