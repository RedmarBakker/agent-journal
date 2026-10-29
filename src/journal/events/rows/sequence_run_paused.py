from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunPaused(SequenceRunEvent):
    """The agent set its sequence aside, saying why."""

    reason: str
