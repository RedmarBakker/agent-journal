from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceRunCancelled(RowEvent):
    """The user ended an agent's sequence, with the run as it stood."""

    feature_name = "sequences"

    agent_session: str
    run: SequenceRun
