from journal.engine.job import Job
from journal.models.agent import Agent
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.supervisor_link import SupervisorLink

SCREEN_TAIL_CHARACTERS = 8192


class ContextLimitCompaction(Job):
    """Twice a second each live agent's screen is read through the supervisor's mirror, and an agent its provider stopped at the context limit, waiting for someone to compact, has the compact command typed into its terminal, once while the notice stays on the screen."""

    interval_seconds = 0.5

    def __init__(self, agents: Agents, providers: Providers, supervisor: SupervisorLink, scope: Scope) -> None:
        self.agents, self.providers, self.supervisor, self.scope = agents, providers, supervisor, scope
        self._compacted: set[int] = set()

    def tick(self, time: float) -> None:
        for agent in self.agents.program_main_agents():
            with self.scope.environment(agent.environment_id):
                self.check(agent)

    def check(self, agent: Agent) -> bool:
        provider, environment = self.providers.lookup(agent.provider), agent.environment_id
        if not provider.is_at_context_limit(self.supervisor.screen(environment)[-SCREEN_TAIL_CHARACTERS:]):
            self._compacted.discard(environment)
            return False
        if environment in self._compacted:
            return False
        self._compacted.add(environment)
        self.supervisor.choose(environment, provider.compact_command)
        return True
