from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceRunTransferred(RowEvent):
    """A run of the last session here that ended was taken over by a new session, as it stood."""

    feature_name = "sequences"

    agent_session: str
    run: SequenceRun
