from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunCannotFinish(SequenceRunEvent):
    """A sequence an agent runs cannot finish, since what it was about is gone."""

    sequence_id: int
    reason: str
