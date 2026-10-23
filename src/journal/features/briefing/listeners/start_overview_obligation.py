from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.repositories.agents import Agents


class StartOverviewObligation(AgentListener[SessionStarted]):
    """Every start of a session but a resume, whose conversation already holds it, requires a read of what is in progress here before any other write: the fact on the agent's row; the briefing conduct enforces it."""

    blocking = True

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: SessionStarted) -> None:
        if event.is_resume():
            return
        self.agents.touch(self.agents.session_agent(event.session), Actor.system(), is_overview_read=False)
