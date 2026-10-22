from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class SlowTick(Event):
    """A job's run that took longer than the job runner allows, announced once it has ended."""

    job: str
    seconds: float
