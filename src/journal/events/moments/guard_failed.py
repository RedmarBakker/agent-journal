from dataclasses import dataclass

from journal.events.moments.fault_moment import FaultMoment


@dataclass(frozen=True, kw_only=True)
class GuardFailed(FaultMoment):
    """A listener raised on an agent's event and the event went through."""

    text: str
