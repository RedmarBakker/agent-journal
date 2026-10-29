from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent


@dataclass(frozen=True, kw_only=True)
class SequenceStepAdopted(SequenceRunEvent):
    """The agent followed the step in hand of its sequence, which takes it up."""

