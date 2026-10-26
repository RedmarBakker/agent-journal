from journal.engine.base_state import BaseState
from journal.engine.states_catalogue import StatesCatalogue
from journal.models.agent import Agent
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.providers.providers import Providers
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.missing_row import MissingRow
from journal.support.rejection import Rejection


class SessionAgents:
    """The agent row of a session and the state on top of its stack: every row is made here, at rest on the floor of its role, idle for the main agent and the helper's own floor for a worker, a verifier or a reviewer, whether a hook, a command or a listener asks first."""

    def __init__(self, agents: Agents, states: StatesCatalogue, providers: Providers) -> None:
        self.agents, self.states, self.providers = agents, states, providers

    def agent(self, session: str, environment_id: int, provider: str | None = None) -> Agent:
        return self.row(session, environment_id, provider, AgentRole.MAIN)

    def caller_agent(self, caller: Caller, session: str, environment_id: int) -> Agent:
        return self.row(session, environment_id, caller.provider, caller.session_role)

    def helper_agent(self, session: str, environment_id: int, provider: str, role: AgentRole) -> Agent:
        return self.row(session, environment_id, provider, role)

    def row(self, session: str, environment_id: int, provider: str | None, role: AgentRole) -> Agent:
        if not session:
            raise Rejection("no agent runs this, so there is no agent to move: only an agent's own session can")
        try:
            return self.agents.session_agent(session)
        except MissingRow:
            bottom = self.states.first() if role == AgentRole.MAIN else self.states.sent_first(role)
            return self.agents.save(Agent(environment_id=environment_id, session=session, provider=provider or self.providers.default().name, state=bottom.name, data=bottom.serialized(), role=role), Actor.system())

    def top(self, session: str) -> BaseState:
        agent = self.agents.session_agent(session)
        return self.states.restored(agent.state, agent.data)
