from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.session_agents import SessionAgents
from journal.events.agent.helper_assignment import HelperAssignment
from journal.events.agent.session_ended import SessionEnded
from journal.events.agent.subagent_ended import SubagentEnded
from journal.helpers.helper_listeners import HelperListeners
from journal.models.environment import Environment
from journal.repositories.agents import Agents
from journal.support.agent_role import AgentRole
from journal.support.hook import Hook
from journal.support.time_source import TimeSource


class ResearcherHooks:
    """A subagent's own row: made at its start in the subagent's role, which puts it to work researching, and put to work again at its start and each of its hooks when its row rests on Void, as one an old end left there does, answering its tool uses as a helper's, and at its end, when it has a row, popped back to Void and ended, as every researcher row of a main session is when that session ends."""

    def __init__(self, sessions: SessionAgents, agents: Agents, listeners: HelperListeners, states: StatesCatalogue, time_source: TimeSource) -> None:
        self.sessions, self.agents, self.listeners, self.states, self.time_source = sessions, agents, listeners, states, time_source

    def bind(self, hook: Hook, environment: Environment) -> None:
        self.sessions.helper_agent(hook.session, environment.row_id, hook.provider, AgentRole.SUBAGENT)
        self.assign_work(hook.session, environment, hook.provider)

    def started(self, hook: Hook, environment: Environment) -> None:
        self.sessions.helper_agent(hook.researcher_session, environment.row_id, hook.provider, AgentRole.SUBAGENT)
        self.assign_work(hook.researcher_session, environment, hook.provider)

    def assign_work(self, session: str, environment: Environment, provider: str) -> None:
        assignment = HelperAssignment(state=self.states.sent_first(AgentRole.SUBAGENT))
        self.listeners.dispatch(assignment.placed(session, environment.row_id, provider, None, self.time_source.seconds()))

    def ended(self, hook: Hook, environment: Environment) -> None:
        if not self.agents.session_rows(hook.researcher_session):
            return
        moment = self.time_source.seconds()
        self.listeners.dispatch(SubagentEnded(subagent=hook.subagent, report=hook.subagent_report).placed(hook.researcher_session, environment.row_id, hook.provider, None, moment))
        self.closed(hook.researcher_session, environment, hook.provider)

    def main_ended(self, hook: Hook, environment: Environment) -> None:
        for researcher in self.agents.researchers(hook.session):
            self.closed(researcher.session, environment, hook.provider)

    def closed(self, session: str, environment: Environment, provider: str) -> None:
        self.listeners.dispatch(SessionEnded().placed(session, environment.row_id, provider, None, self.time_source.seconds()))
