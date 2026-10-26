from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class SequenceStepAdopted(RowEvent):
    """The agent followed the step in hand of its sequence, which takes it up."""

    feature_name = "sequences"

    agent_session: str
