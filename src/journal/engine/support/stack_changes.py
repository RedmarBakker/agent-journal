from journal.engine.support.stack_history import StackHistory
from journal.events.bus import Bus
from journal.events.stack_moved import StackMoved
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class StackChanges:
    """A move of an agent's stack written once: the entry the trail shows, and StackMoved announced with the top before, the top after and the cause."""

    def __init__(self, entries: Entries, bus: Bus, time_source: TimeSource) -> None:
        self.entries, self.bus, self.time_source = entries, bus, time_source

    def moved(self, agent: Agent, following: list[dict], cause: str, actor: Actor) -> None:
        self.entries.save(StackHistory.entry(agent, following, cause, actor), actor)
        before, after = (agent.stack or ({},))[-1].get("state", ""), (following or [{}])[-1].get("state", "")
        self.bus.dispatch(StackMoved(before_state=before, after_state=after, cause=cause, at=self.time_source.seconds()))
