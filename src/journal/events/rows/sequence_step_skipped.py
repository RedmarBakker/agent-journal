from dataclasses import dataclass

from journal.events.rows.sequence_step_moved import SequenceStepMoved


@dataclass(frozen=True, kw_only=True)
class SequenceStepSkipped(SequenceStepMoved):
    """The user skipped the step in hand of an agent's sequence, with the run as it stood."""
