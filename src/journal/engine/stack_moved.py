from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.events.event import Event
from journal.models.agent import Agent


@dataclass(frozen=True, kw_only=True)
class StackMoved(Event):
    """An agent's stack changed: the agent as it was, the state on top before, the state on top after, the event that caused it, when, and the states the move removed, with the wait seconds they count against the agent."""

    agent: Agent
    old_top: str
    new_top: str
    cause: str
    moved_at: float
    removed_states: tuple[BaseState, ...]

    def counted_wait_seconds(self, uncounted_seconds: int) -> int:
        return sum(state.counted_wait_seconds(self.moved_at, uncounted_seconds) for state in self.removed_states)
