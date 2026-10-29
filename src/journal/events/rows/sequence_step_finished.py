from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceStepFinished(SequenceRunEvent):
    """The agent finished the step in hand of its sequence: the run as it was before the step was finished."""

    run: SequenceRun
