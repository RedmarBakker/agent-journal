from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceStepMoved(SequenceRunEvent):
    """The step in hand of an agent's sequence was left behind, finished by the agent or skipped by the user, with the run as it stood before."""

    run: SequenceRun
