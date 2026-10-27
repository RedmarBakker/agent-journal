from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.thinking.support.thinking_window import ThinkingWindow
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.support.actor import Actor

# the moves that start or end a quiet spell of the agent's
MOVES = ("ToolStarting", "ToolFinished", "PromptSubmitted", "Stop")


class ThinkingWatch(AgentListener[Ticked]):
    """At every clock tick, marks the agent thinking once its quiet spell opens the thinking window, and no longer once it closes; each change is an event of its own."""

    def __init__(self, agents: Agents, entries: Entries) -> None:
        self.agents, self.entries = agents, entries

    def handle(self, event: Ticked) -> None:
        agent = self.agents.session_agent(event.session)
        moves = self.entries.session_moves(MOVES, event.session)
        last = moves[0] if moves else None
        thinking = bool(last) and ThinkingWindow.opens(agent.state, last.entry_type, event.time - last.created_at.timestamp())
        if thinking and not agent.is_thinking():
            self.agents.save(agent.thinking_started(event.time), Actor.system())
        elif agent.is_thinking() and not thinking:
            self.agents.save(agent.thinking_ended(event.time), Actor.system())
