from journal.engine.support.stack_history import StackHistory
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.repositories.state_transitions import StateTransitions
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class StackChanges:
    """A move of an agent's stack written once: the entry the trail shows, and one more of its kind counted, the top before, the top after and the cause."""

    def __init__(self, entries: Entries, transitions: StateTransitions, time_source: TimeSource) -> None:
        self.entries, self.transitions, self.time_source = entries, transitions, time_source

    def moved(self, agent: Agent, following: list[dict], cause: str, actor: Actor) -> None:
        self.entries.save(StackHistory.entry(agent, following, cause, actor), actor)
        before, after = (agent.stack or ({},))[-1].get("state", ""), (following or [{}])[-1].get("state", "")
        self.transitions.counted(before, after, cause, self.time_source.seconds(), actor)
