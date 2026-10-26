from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceStepFinished(RowEvent):
    """The agent finished the step in hand of its sequence: the run as it was before the step was finished."""

    feature_name = "sequences"

    agent_session: str
    run: SequenceRun
