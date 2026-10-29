from dataclasses import dataclass

from journal.events.rows.sequence_run_event import SequenceRunEvent
from journal.support.sequence_run import SequenceRun


@dataclass(frozen=True, kw_only=True)
class SequenceRunStarted(SequenceRunEvent):
    """A sequence was started for an agent, by its session, with the run it begins."""

    run: SequenceRun
