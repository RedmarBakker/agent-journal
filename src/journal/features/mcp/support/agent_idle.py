from journal.chat.turn import Turn
from journal.models.agent import Agent
from journal.repositories.scope import Scope
from journal.repositories.subagents import Subagents
from journal.repositories.workers import Workers


class AgentIdle:
    """Whether an agent can be restarted: its turn has ended and no subagent of it and no worker in its environment is running."""

    def __init__(self, turn: Turn, subagents: Subagents, workers: Workers, scope: Scope) -> None:
        self.turn, self.subagents, self.workers, self.scope = turn, subagents, workers, scope

    def is_idle(self, agent: Agent) -> bool:
        if not self.turn.is_finished(agent):
            return False
        with self.scope.environment(agent.environment_id):
            return not self.subagents.running_session_subagents(agent.session) and not self.workers.running_workers()
