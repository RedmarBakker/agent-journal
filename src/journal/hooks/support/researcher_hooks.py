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
from journal.models.agent import Agent
from journal.support.time_source import TimeSource


class ResearcherHooks:
    """A subagent's own row: made at its start in the subagent's role, which puts it to work researching, and put to work again at its start and each of its hooks when its row rests on Void, as one an old end left there does, answering its tool uses as a helper's, and at its end, when it has a row, popped back to Void and ended, as every researcher row of a main session is when that session ends."""

    def __init__(self, sessions: SessionAgents, agents: Agents, listeners: HelperListeners, states: StatesCatalogue, time_source: TimeSource) -> None:
        self.sessions, self.agents, self.listeners, self.states, self.time_source = sessions, agents, listeners, states, time_source

    def bind(self, hook: Hook, environment: Environment) -> Agent:
        agent = self.sessions.helper_agent(hook.session, environment.row_id, hook.provider, AgentRole.SUBAGENT)
        self.assign_work(agent)
        return agent

    def started(self, hook: Hook, environment: Environment) -> None:
        self.assign_work(self.sessions.helper_agent(hook.researcher_session, environment.row_id, hook.provider, AgentRole.SUBAGENT))

    def assign_work(self, agent: Agent) -> None:
        self.listeners.dispatch(HelperAssignment(state=self.states.sent_first(AgentRole.SUBAGENT), agent=agent).placed(agent, None, self.time_source.seconds()))

    def ended(self, hook: Hook, environment: Environment) -> None:
        researchers = self.agents.session_rows(hook.researcher_session)
        if not researchers:
            return
        self.listeners.dispatch(SubagentEnded(subagent=hook.subagent, report=hook.subagent_report, agent=researchers[0]).placed(researchers[0], None, self.time_source.seconds()))
        self.closed(researchers[0])

    def main_ended(self, hook: Hook, environment: Environment) -> None:
        for researcher in self.agents.researchers(hook.session):
            self.closed(researcher)

    def closed(self, researcher: Agent) -> None:
        self.listeners.dispatch(SessionEnded(agent=researcher).placed(researcher, None, self.time_source.seconds()))
