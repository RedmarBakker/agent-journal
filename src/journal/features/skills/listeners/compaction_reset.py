from journal.events.agent.compacting import Compacting
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.repositories.agents import Agents


class CompactionReset(AgentListener[Compacting]):
    """A compacted window no longer contains the skills it read; they must be read again."""

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: Compacting) -> None:
        self.agents.rewritten(event.agent, Actor.system(), lambda row: row.with_(skills_loaded={}))
