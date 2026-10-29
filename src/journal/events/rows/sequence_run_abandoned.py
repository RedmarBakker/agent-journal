from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunAbandoned(SequenceRunEvent):
    """The agent gave its sequence up, its remaining steps undone."""

    reason: str
