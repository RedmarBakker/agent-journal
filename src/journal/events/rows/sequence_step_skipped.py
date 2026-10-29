from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceStepSkipped(SequenceRunEvent):
    """The user skipped the step in hand of an agent's sequence, with the run as it stood."""

    run: SequenceRun
