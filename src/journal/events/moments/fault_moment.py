from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class FaultMoment(Event):
    """Something went wrong in the journal's handling of an agent's session, in the environment whose chat shows it."""

    environment_id: int
    session: str
