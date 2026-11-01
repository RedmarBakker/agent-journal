from journal.engine.base_state import BaseState
from journal.engine.support.stack import Stack
from journal.events.rows.worker_agent_created import WorkerAgentCreated
from journal.engine.states_catalogue import StatesCatalogue
from journal.models.agent import Agent
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.providers.providers import Providers
from journal.engine.support.session_takeovers import SessionTakeovers
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.caller import Caller


class SessionAgents:
    """The agent row of a session and the state on top of its stack: every row is made here, at rest on the floor of its role, idle for the main agent and the helper's own floor for a worker, a verifier or a reviewer, whether a hook, a command or a listener asks first."""

    def __init__(self, agents: Agents, states: StatesCatalogue, providers: Providers, takeovers: SessionTakeovers) -> None:
        self.agents, self.states, self.providers, self.takeovers = agents, states, providers, takeovers

    def agent(self, session: str, environment_id: int, provider: str | None = None, session_started: bool = False) -> Agent:
        return self.row(session, environment_id, provider, AgentRole.MAIN, session_started)

    def caller_agent(self, caller: Caller, session: str, environment_id: int) -> Agent:
        return self.row(session, environment_id, caller.provider, caller.session_role)

    def helper_agent(self, session: str, environment_id: int, provider: str, role: AgentRole) -> Agent:
        return self.row(session, environment_id, provider, role)

    def row(self, session: str, environment_id: int, provider: str | None, role: AgentRole, session_started: bool = False) -> Agent:
        rows = self.session_rows(session)
        if rows:
            return rows[0]
        current = self.agents.environment_main_agent(environment_id)
        if current is not None:
            if session_started and current.session and current.session != session:
                self.takeovers.remember(environment_id, session, current.update_time)
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
        if rows and rows[0].role == AgentRole.WORKER and rows[0].environment_id == environment_id:
            return rows[0]
        worker_row = self.unsaved(session, environment_id, provider, self.states.helper_layers(self.states.sent_first(AgentRole.WORKER)), AgentRole.WORKER)
        if rows:
            worker_row = rows[0].with_(environment_id=worker_row.environment_id, provider=worker_row.provider,
                                       state=worker_row.state, data=worker_row.data, stack=worker_row.stack,
                                       role=worker_row.role)
        return self.agents.save(worker_row.with_event(WorkerAgentCreated(agent_session=session)), Actor.system())

    def created(self, session: str, environment_id: int, provider: str | None, layers: Stack, role: AgentRole) -> Agent:
        return self.agents.save(self.unsaved(session, environment_id, provider, layers, role), Actor.system())

    def unsaved(self, session: str, environment_id: int, provider: str | None, layers: Stack, role: AgentRole) -> Agent:
        top = layers.top()
        return Agent(environment_id=environment_id, session=session, provider=provider or self.providers.default().name, state=top.name, data=top.serialized(), stack=tuple(layers.serialized()), role=role)

    def top(self, session: str) -> BaseState:
        return self.states.top(self.agents.session_agent(session))

    def blocks_tools(self, session: str) -> bool:
        return any(self.states.restored(layer["state"], layer.get("data", {})).blocks_tools() for layer in self.agents.session_agent(session).stack)
