from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.session_agents import SessionAgents
from journal.events.agent.helper_assignment import HelperAssignment
from journal.events.agent.session_ended import SessionEnded
from journal.events.agent.subagent_ended import SubagentEnded
from journal.helpers.role_listeners import RoleListeners
from journal.models.environment import Environment
from journal.repositories.agents import Agents
from journal.support.agent_role import AgentRole
from journal.support.hook import Hook
from journal.support.researcher_session import ResearcherSession
from journal.events.agent.subagent_started import SubagentStarted
from journal.models.agent import Agent
from journal.support.time_source import TimeSource


class ResearcherHooks:
    """A subagent's own row: made at its start in the subagent's role, which puts it to work researching, and put to work again at its start and each of its hooks when its row rests on Void, as one an old end left there does, answering its tool uses as a helper's, and at its end, when it has a row, popped back to Void and ended, as every researcher row of a main session is when that session ends."""

    def __init__(self, sessions: SessionAgents, agents: Agents, listeners: RoleListeners, states: StatesCatalogue, time_source: TimeSource) -> None:
        self.sessions, self.agents, self.listeners, self.states, self.time_source = sessions, agents, listeners, states, time_source

    def bind(self, hook: Hook, environment: Environment) -> Agent:
        agent = self.sessions.helper_agent(hook.session, environment.row_id, hook.provider, AgentRole.SUBAGENT)
        self.assign_work(agent)
        return agent

    def started(self, event: SubagentStarted) -> None:
        self.assign_work(self.sessions.helper_agent(ResearcherSession.joined(event.session, event.subagent), event.environment_id, event.provider, AgentRole.SUBAGENT))

    def assign_work(self, agent: Agent) -> None:
        self.listeners.dispatch(HelperAssignment(state=self.states.sent_first(AgentRole.SUBAGENT), agent=agent).placed(agent, None, self.time_source.seconds()))

    def ended(self, event: SubagentEnded) -> None:
        researchers = self.agents.session_rows(ResearcherSession.joined(event.session, event.subagent))
        if not researchers:
            return
        self.listeners.dispatch(SubagentEnded(subagent=event.subagent, report=event.report, agent=researchers[0]).placed(researchers[0], None, self.time_source.seconds()))
        self.closed(researchers[0])

    def main_ended(self, event: SessionEnded) -> None:
        for researcher in self.agents.researchers(event.session):
            self.closed(researcher)

    def closed(self, researcher: Agent) -> None:
        self.listeners.dispatch(SessionEnded(agent=researcher).placed(researcher, None, self.time_source.seconds()))
