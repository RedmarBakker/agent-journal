from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class SyncMoment(Event):
    """Something the team sync did or found, in the environment whose chat shows it."""

    environment_id: int
