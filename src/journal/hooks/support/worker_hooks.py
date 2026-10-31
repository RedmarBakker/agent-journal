from journal.engine.support.session_agents import SessionAgents
from journal.events.rows.worker_session_bound import WorkerSessionBound
from journal.models.environment import Environment
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.hook import Hook
from journal.models.agent import Agent
from journal.hooks.support.agent_identity import AgentIdentity


class WorkerHooks:
    """A worker hook is identified by its token or bound session, and its session and agent row follow the worker's current provider session."""

    def __init__(self, identity: AgentIdentity, workers: Workers, agents: SessionAgents) -> None:
        self.identity, self.workers, self.agents = identity, workers, agents

    def attributed(self, hook: Hook) -> Hook:
        owners = self.workers.global_matching(session=hook.session) if hook.worker is None and hook.session else []
        return hook.worker_hook(owners[0].id, None) if owners else hook

    def is_proven(self, hook: Hook) -> bool:
        return hook.worker is not None and (self.identity.is_token(hook.worker, hook.actor_token) or self.is_worker_session(hook))

    def is_worker_session(self, hook: Hook) -> bool:
        return any(row.session == hook.session for row in self.workers.global_matching(id=hook.worker))

    def bind(self, hook: Hook, environment: Environment) -> Agent:
        worker = self.workers.find(hook.worker)
        if worker.session != hook.session:
            bound = worker.with_(session=hook.session, resume=hook.session)
            self.workers.save(bound.with_event(WorkerSessionBound(environment_id=worker.environment_id)), Actor.system())
        return self.agents.worker_agent(hook.session, environment.row_id, hook.provider)
