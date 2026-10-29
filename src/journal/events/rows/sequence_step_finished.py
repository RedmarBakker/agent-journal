from dataclasses import dataclass

from journal.events.rows.sequence_step_moved import SequenceStepMoved


@dataclass(frozen=True, kw_only=True)
class SequenceStepFinished(SequenceStepMoved):
    """The agent finished the step in hand of its sequence: the run as it was before the step was finished."""
