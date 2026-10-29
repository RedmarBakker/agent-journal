from dataclasses import replace

from journal.engine.support.session_agents import SessionAgents
from journal.hooks.support.checker_hooks import CheckerHooks
from journal.hooks.support.researcher_hooks import ResearcherHooks
from journal.hooks.support.worker_hooks import WorkerHooks
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.support.hook import Hook
from journal.support.researcher_session import ResearcherSession


class HookSeats:
    """The agent row a hook or a command belongs to, found once at the door: a worker's, a verifier's or a reviewer's bound to its row, a researcher's made for it, else the main agent's; a command from an agent's shell that names no session is the present agent's."""

    def __init__(self, sessions: SessionAgents, workers: WorkerHooks, checkers: CheckerHooks, researchers: ResearcherHooks, agents: Agents, scope: Scope) -> None:
        self.sessions, self.workers, self.checkers, self.researchers, self.agents, self.scope = sessions, workers, checkers, researchers, agents, scope

    def agent(self, hook: Hook, environment: Environment) -> Agent:
        if hook.researcher:
            return self.researchers.bind(hook, environment)
        if hook.worker is not None:
            return self.workers.bind(hook, environment)
        if hook.is_sent():
            return self.checkers.bind(hook, environment)
        return self.sessions.agent(hook.session, environment.row_id, hook.provider)

    def is_unknown_session_end(self, hook: Hook) -> bool:
        return hook.is_session_end() and not self.agents.matching(session=hook.session)

    def caller_seated(self, caller: Caller) -> Caller:
        attributed = self.attributed(caller)
        if not attributed.session:
            return attributed
        researchers = self.researcher_rows(attributed) if attributed.subagent else []
        if researchers:
            return replace(attributed, agent_row=researchers[-1])
        rows = self.agents.session_rows(attributed.session)
        if rows:
            return replace(attributed, agent_row=rows[0])
        return self.helper_seated(attributed) if attributed.session_role.is_helper() else attributed

    def researcher_rows(self, caller: Caller) -> list[Agent]:
        if caller.subagent_session:
            return self.agents.session_rows(ResearcherSession.joined(caller.session, caller.subagent_session))
        return self.agents.researchers(caller.session)

    def helper_seated(self, caller: Caller) -> Caller:
        if caller.is_worker():
            return replace(caller, agent_row=self.sessions.worker_agent(caller.session, self.scope.id, caller.provider))
        return replace(caller, agent_row=self.sessions.helper_agent(caller.session, self.scope.id, caller.provider, caller.session_role))

    def attributed(self, caller: Caller) -> Caller:
        if not caller.is_unnamed_agent():
            return caller
        present = self.agents.current()
        return replace(caller, session=present.session, provider=present.provider) if present else caller
