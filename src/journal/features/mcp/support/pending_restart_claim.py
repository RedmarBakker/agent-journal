from journal.features.mcp.support.agent_idle import AgentIdle
from journal.repositories.agents import Agents
from journal.support.pending_restarts import PendingRestarts
from journal.supervisor_link import SupervisorLink


class PendingRestartClaim:
    """Restarts the agent of a session whose restart is waiting, once it is idle."""

    def __init__(self, pending: PendingRestarts, idle: AgentIdle, agents: Agents, supervisor: SupervisorLink) -> None:
        self.pending, self.idle, self.agents, self.supervisor = pending, idle, agents, supervisor

    def restarted(self, session: str) -> None:
        if session not in self.pending.sessions():
            return
        agent = next((main for main in self.agents.active_main_agents() if main.session == session), None)
        if agent is None or not self.idle.is_idle(agent):
            return
        claimed = self.pending.claim(session)
        if claimed:
            self.supervisor.restart_agent(claimed[0], claimed[1])
