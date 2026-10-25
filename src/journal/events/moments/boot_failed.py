from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class BootFailed(Event):
    """A boot of this journal failed in a way it went on from: a seed that raised and was skipped, or a boot the supervisor started again or took back to the last version that booted."""

    text: str
    time: float
