from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.support.actor import Actor

KIND = "workload_level"


class LevelEntries:
    """The level of the workload an agent was last informed past, recorded as an entry of its session whenever it changes."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def latest(self, session: str) -> float:
        newest = self.entries.session_kind_newest(session, KIND, 1)
        return float(newest[0].data["level"]) if newest else 0.0

    def record(self, agent: Agent, level: float) -> None:
        if level != self.latest(agent.session):
            self.entries.save(Entry(environment_id=agent.environment_id, kind=KIND, actor=Actor.system(), data={"session": agent.session, "level": level}), Actor.system())
