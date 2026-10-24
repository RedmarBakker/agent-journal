from dataclasses import dataclass

from journal.events.moments.fault_moment import FaultMoment


@dataclass(frozen=True, kw_only=True)
class SessionUnbound(FaultMoment):
    """A session started without the launch id of the environment it ran in, so the journal records its hooks and does not take it as that environment's agent."""

    environment: str
