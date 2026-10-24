from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class SequenceAbandoned(Event):
    """The agent gave a sequence's run up at a step, with why, and the steps it left undone."""

    environment_id: int
    session: str
    sequence_id: int
    title: str
    step: int
    explanation: str
    skipped: str
