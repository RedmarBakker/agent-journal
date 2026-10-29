from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class ThinkingStop(AgentListener[ToolStarting]):
    """A tool starting ends the agent's thinking at once, without waiting for the next clock tick."""

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: ToolStarting) -> None:
        if event.agent.is_thinking():
            self.agents.rewritten(event.agent, Actor.system(), lambda row: row.thinking_ended(event.time))
