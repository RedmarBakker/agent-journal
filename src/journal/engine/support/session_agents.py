from journal.engine.base_state import BaseState
from journal.engine.support.stack import Stack
from journal.events.rows.worker_agent_created import WorkerAgentCreated
from journal.engine.states_catalogue import StatesCatalogue
from journal.models.agent import Agent
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.providers.providers import Providers
from journal.support.actor import Actor
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
        return self.created(session, environment_id, provider, Stack((self.states.first(),)), AgentRole.MAIN)

    def helper_agent(self, session: str, environment_id: int, provider: str | None, role: AgentRole) -> Agent:
        rows = self.session_rows(session)
        return rows[0] if rows else self.created(session, environment_id, provider, self.states.helper_layers(self.states.sent_first(role)), role)

    def session_rows(self, session: str) -> list[Agent]:
        if not session:
            raise Rejection("no agent runs this, so there is no agent to move: only an agent's own session can")
        return self.agents.session_rows(session)

    def worker_agent(self, session: str, environment_id: int, provider: str | None) -> Agent:
        rows = self.session_rows(session)
        if rows:
            return rows[0]
        worker_row = self.unsaved(session, environment_id, provider, self.states.helper_layers(self.states.sent_first(AgentRole.WORKER)), AgentRole.WORKER)
        return self.agents.save(worker_row.with_event(WorkerAgentCreated(agent_session=session)), Actor.system())

    def created(self, session: str, environment_id: int, provider: str | None, layers: Stack, role: AgentRole) -> Agent:
        return self.agents.save(self.unsaved(session, environment_id, provider, layers, role), Actor.system())

    def unsaved(self, session: str, environment_id: int, provider: str | None, layers: Stack, role: AgentRole) -> Agent:
        top = layers.top()
        return Agent(environment_id=environment_id, session=session, provider=provider or self.providers.default().name, state=top.name, data=top.serialized(), stack=tuple(layers.serialized()), role=role)

    def top(self, session: str) -> BaseState:
        agent = self.agents.session_agent(session)
        return self.states.restored(agent.state, agent.data)

    def blocks_tools(self, session: str) -> bool:
        return any(self.states.restored(layer["state"], layer.get("data", {})).blocks_tools() for layer in self.agents.session_agent(session).stack)
