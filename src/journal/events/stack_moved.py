from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class StackMoved(Event):
    """An agent's stack changed: the state on top before, the state on top after and the event that caused it."""

    before_state: str
    after_state: str
    cause: str
    at: float
