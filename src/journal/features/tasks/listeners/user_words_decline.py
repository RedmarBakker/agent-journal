from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent_listener import AgentListener
from journal.engine.support.session_agents import SessionAgents
from journal.features.tasks.states.choosing_paused_work import CHOOSING_PAUSED_WORK
from journal.repositories.agents import Agents
from journal.support.actor import Actor
from journal.events.blocking import Blocking


class UserWordsDecline(AgentListener[PromptSubmitted]):
    """The user's own words while the agent chooses its paused work set that work aside until the next close: the user said what comes next."""

    blocking = Blocking.NEXT_DECISION

    def __init__(self, sessions: SessionAgents, agents: Agents) -> None:
        self.sessions, self.agents = sessions, agents

    def handle(self, event: PromptSubmitted) -> None:
        agent = self.sessions.agent(event.session, event.environment_id)
        if event.is_users and agent.stack and agent.stack[-1].get("state") == CHOOSING_PAUSED_WORK:
            self.agents.rewritten(agent, Actor.system(), lambda current: current.paused_work_declined(event.time))
