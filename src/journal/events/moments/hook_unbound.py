from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class HookUnbound(Event):
    """A hook of a session that ran without the launch id of the environment it ran in: recorded, never taken as that environment's agent."""

    environment_id: int
    session: str
    environment: str
