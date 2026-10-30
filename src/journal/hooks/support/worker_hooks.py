from journal.engine.support.session_agents import SessionAgents
from journal.events.rows.worker_session_bound import WorkerSessionBound
from journal.models.environment import Environment
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.hook import Hook
from journal.models.agent import Agent
from journal.hooks.support.agent_identity import AgentIdentity


class WorkerHooks:
    """A hook from a worker's run: named a worker's by its session when it carries no worker header, taken in by the worker's token or its own session in place of the launch id, its session bound to the worker's row when the row names none yet, and its agent row made in the worker's role."""

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
        if not worker.session:
            self.workers.save(worker.with_(session=hook.session).with_event(WorkerSessionBound(environment_id=worker.environment_id)), Actor.system())
        return self.agents.worker_agent(hook.session, environment.row_id, hook.provider)
