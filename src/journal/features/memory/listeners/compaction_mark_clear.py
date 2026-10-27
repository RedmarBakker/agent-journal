from journal.events.agent.compacting import Compacting
from journal.events.agent_listener import AgentListener
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class CompactionMarkClear(AgentListener[Compacting]):
    """A compaction ends the window a mark was owed in, so the mark owed is cleared; the marks start again with the first reading of the new window."""

    blocking = True

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: Compacting) -> None:
        agent = self.agents.session_agent(event.session)
        if agent.threshold_due:
            self.agents.touch(agent, Actor.system(), threshold_due=0)
