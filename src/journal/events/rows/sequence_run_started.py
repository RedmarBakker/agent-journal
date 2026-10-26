from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceRunStarted(RowEvent):
    """A sequence was started for an agent, by its session, with the run it begins."""

    feature_name = "sequences"

    agent_session: str
    run: SequenceRun
