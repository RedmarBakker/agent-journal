from datetime import datetime

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
from journal.support.time_source import TimeSource


class SessionAgents:
    """The agent row of a session and the state on top of its stack: every row is made here, at rest on the floor of its role, idle for the main agent and the helper's own floor for a worker, a verifier or a reviewer, whether a hook, a command or a listener asks first."""

    def __init__(self, agents: Agents, states: StatesCatalogue, providers: Providers, takeovers: SessionTakeovers, time_source: TimeSource) -> None:
        self.agents, self.states, self.providers, self.takeovers, self.time_source = agents, states, providers, takeovers, time_source

    def agent(self, session: str, environment_id: int, provider: str | None = None) -> Agent:
        return self.row(session, environment_id, provider, AgentRole.MAIN)

    def started_agent(self, session: str, environment_id: int, provider: str | None = None) -> Agent:
        return self.row(session, environment_id, provider, AgentRole.MAIN, self.time_source.moment())

    def caller_agent(self, caller: Caller, session: str, environment_id: int) -> Agent:
        return self.row(session, environment_id, caller.provider, caller.session_role)

    def helper_agent(self, session: str, environment_id: int, provider: str, role: AgentRole) -> Agent:
        return self.row(session, environment_id, provider, role)

    def row(self, session: str, environment_id: int, provider: str | None, role: AgentRole, started_at: datetime | None = None) -> Agent:
        rows = self.session_rows(session)
        current = self.persistent_main_agent(environment_id)
        if current and (not rows or rows[0].environment_id == environment_id):
            return self.reused(current, session, environment_id, provider, started_at)
        if rows:
            current = rows[0]
            return self.agents.save(current.session_started(started_at), Actor.system()) if started_at and not current.session_started_at else current
        current = self.agents.environment_main_agent(environment_id)
        if current is not None:
            return self.reused(current, session, environment_id, provider, started_at)
        return self.created(session, environment_id, provider, Stack((self.states.first(),)), AgentRole.MAIN, started_at)

    def persistent_main_agent(self, environment_id: int) -> Agent | None:
        return next((agent for agent in self.agents.main_scoped(environment_id) if self.states.stack(agent).bottom().keeps_floor()), None)

    def reused(self, current: Agent, session: str, environment_id: int, provider: str | None, started_at: datetime | None) -> Agent:
        if current.session == session:
            return self.agents.save(current.session_started(started_at), Actor.system()) if started_at and not current.session_started_at else current
        if started_at and current.session:
            self.takeovers.remember(environment_id, session, current.update_time)
        changed = current.with_session(session, provider or current.provider)
        if started_at:
            changed = changed.session_started(started_at)
        return self.agents.save(changed, Actor.system())

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

    def created(self, session: str, environment_id: int, provider: str | None, layers: Stack, role: AgentRole, started_at: datetime | None = None) -> Agent:
        return self.agents.save(self.unsaved(session, environment_id, provider, layers, role, started_at), Actor.system())

    def unsaved(self, session: str, environment_id: int, provider: str | None, layers: Stack, role: AgentRole, started_at: datetime | None = None) -> Agent:
        top = layers.top()
        return Agent(environment_id=environment_id, session=session, provider=provider or self.providers.default().name, state=top.name, data=top.serialized(), stack=tuple(layers.serialized()), role=role, session_started_at=started_at)

    def top(self, session: str) -> BaseState:
        return self.states.top(self.agents.session_agent(session))

    def blocks_tools(self, session: str) -> bool:
        return any(self.states.restored(layer["state"], layer.get("data", {})).blocks_tools() for layer in self.agents.session_agent(session).stack)
