from journal.engine.support.session_agents import SessionAgents
from journal.models.environment import Environment
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.hook import Hook
from journal.features.workers.support.worker_identity import WorkerIdentity


class WorkerHooks:
    """A hook from a worker's run: named a worker's by its session when it carries no worker header, taken in by the worker's token or its own session in place of the launch id, its session bound to the worker's row when the row names none yet, and its agent row made in the worker role."""

    def __init__(self, identity: WorkerIdentity, workers: Workers, agents: SessionAgents) -> None:
        self.identity, self.workers, self.agents = identity, workers, agents

    def named(self, hook: Hook) -> Hook:
        owners = self.workers.global_matching(session=hook.session) if hook.worker is None and hook.session else []
        return hook.worker_hook(owners[0].id, None) if owners else hook

    def is_proven(self, hook: Hook) -> bool:
        return hook.worker is not None and (self.identity.is_token(hook.worker, hook.worker_token) or self.is_own_session(hook))

    def is_own_session(self, hook: Hook) -> bool:
        return any(row.session == hook.session for row in self.workers.global_matching(id=hook.worker))

    def bind(self, hook: Hook, environment: Environment) -> None:
        if hook.worker is None:
            return
        worker = self.workers.find(hook.worker)
        if not worker.session:
            self.workers.save(worker.with_(session=hook.session), Actor.system())
        self.agents.worker_agent(hook.session, environment.row_id, hook.provider)
