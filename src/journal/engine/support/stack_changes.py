from journal.engine.base_state import BaseState
from journal.engine.support.stack_history import StackHistory
from journal.events.bus import Bus
from journal.engine.stack_moved import StackMoved
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class StackChanges:
    """A move of an agent's stack written once: the entry the trail shows, and StackMoved announced with the top before, the top after, the cause and the states the move removed."""

    def __init__(self, entries: Entries, bus: Bus, time_source: TimeSource) -> None:
        self.entries, self.bus, self.time_source = entries, bus, time_source

    def moved(self, agent: Agent, following: list[dict], cause: str, actor: Actor, removed_states: tuple[BaseState, ...]) -> None:
        self.entries.save(StackHistory.entry(agent, following, cause, actor), actor)
        old_top, new_top = (agent.stack or ({},))[-1].get("state", ""), (following or [{}])[-1].get("state", "")
        self.bus.dispatch(StackMoved(agent=agent, old_top=old_top, new_top=new_top, cause=cause, moved_at=self.time_source.seconds(), removed_states=removed_states))
