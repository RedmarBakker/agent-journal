from journal.engine.support.session_agents import SessionAgents
from journal.hooks.support.checker_hooks import CheckerHooks
from journal.hooks.support.researcher_hooks import ResearcherHooks
from journal.hooks.support.worker_hooks import WorkerHooks
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.repositories.agents import Agents
from journal.support.hook import Hook


class HookSeats:
    """The agent row a hook belongs to, found once at the door: a worker's, a verifier's or a reviewer's bound to its row, a researcher's made for it, else the main agent's."""

    def __init__(self, sessions: SessionAgents, workers: WorkerHooks, checkers: CheckerHooks, researchers: ResearcherHooks, agents: Agents) -> None:
        self.sessions, self.workers, self.checkers, self.researchers, self.agents = sessions, workers, checkers, researchers, agents

    def agent(self, hook: Hook, environment: Environment) -> Agent:
        if hook.worker is not None:
            return self.workers.bind(hook, environment)
        if hook.is_sent():
            return self.checkers.bind(hook, environment)
        return self.sessions.agent(hook.session, environment.row_id, hook.provider)

    def researcher_agent(self, hook: Hook, environment: Environment) -> Agent:
        return self.researchers.bind(hook, environment)

    def is_unknown_session_end(self, hook: Hook) -> bool:
        return hook.is_session_end() and not self.agents.matching(session=hook.session)
