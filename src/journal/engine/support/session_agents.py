from journal.engine.base_state import BaseState
from journal.engine.states_catalogue import StatesCatalogue
from journal.models.agent import Agent
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.providers.providers import Providers
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class SessionAgents:
    """The agent row of a session and the state on top of its stack: every row is made here, at rest on the floor of its role, idle for the main agent and the helper's own floor for a worker, a verifier or a reviewer, whether a hook, a command or a listener asks first."""

    def __init__(self, agents: Agents, states: StatesCatalogue, providers: Providers) -> None:
        self.agents, self.states, self.providers = agents, states, providers

    def agent(self, session: str, environment_id: int, provider: str | None = None) -> Agent:
        rows = self.session_rows(session)
        if rows:
            return rows[0]
        current = self.agents.environment_main_agent(environment_id)
        if current is not None:
            return self.agents.save(current.with_session(session, provider or current.provider), Actor.system())
        return self.created(session, environment_id, provider, self.states.first(), AgentRole.MAIN)

    def caller_agent(self, caller: Caller, session: str, environment_id: int) -> Agent:
        if caller.session_role.is_helper():
            return self.helper_agent(session, environment_id, caller.provider, caller.session_role)
        return self.agent(session, environment_id, caller.provider)

    def helper_agent(self, session: str, environment_id: int, provider: str | None, role: AgentRole) -> Agent:
        rows = self.session_rows(session)
        return rows[0] if rows else self.created(session, environment_id, provider, self.states.sent_first(role), role)

    def session_rows(self, session: str) -> list[Agent]:
        if not session:
            raise Rejection("no agent runs this, so there is no agent to move: only an agent's own session can")
        return self.agents.session_rows(session)

    def created(self, session: str, environment_id: int, provider: str | None, bottom: BaseState, role: AgentRole) -> Agent:
        return self.agents.save(Agent(environment_id=environment_id, session=session, provider=provider or self.providers.default().name, state=bottom.name, data=bottom.serialized(), role=role), Actor.system())

    def top(self, session: str) -> BaseState:
        agent = self.agents.session_agent(session)
        return self.states.restored(agent.state, agent.data)

    def blocks_tools(self, session: str) -> bool:
        return any(self.states.restored(layer["state"], layer.get("data", {})).blocks_tools() for layer in self.agents.session_agent(session).stack)
