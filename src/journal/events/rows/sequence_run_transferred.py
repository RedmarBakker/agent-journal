from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceRunTransferred(SequenceRunEvent):
    """A run of the last session here that ended was taken over by a new session, as it stood."""

    run: SequenceRun
