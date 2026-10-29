from journal.engine.agent_launcher import AgentLauncher
from journal.engine.base_state import BaseState
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.supervisor_link import SupervisorLink


class AgentEnvironments:
    """An agent of its own in an environment of its own, for a plan or a task outside every plan: the environment made by whoever starts the work and seen as the work's own environment is, shared with its team or private; its one agent row prepared on the floor the work gives it, on the provider of the main agent that started it, launched in a worktree of the environment's name carrying on its last conversation, and stopped."""

    def __init__(self, agents: Agents, environments: Environments, launcher: AgentLauncher, supervisor: SupervisorLink, providers: Providers) -> None:
        self.agents, self.environments, self.launcher, self.supervisor, self.providers = agents, environments, launcher, supervisor, providers

    def made(self, name: str, source_environment_id: int, actor: Actor) -> Environment:
        return self.visible(self.environments.made(name, actor), source_environment_id, actor)

    def visible(self, environment: Environment, source_environment_id: int, actor: Actor) -> Environment:
        source = self.environments.find(source_environment_id)
        team_key = "" if source.is_private() else source.team_key
        if environment.team_key == team_key:
            return environment
        return self.environments.save(environment.shared_with_team(team_key) if team_key else environment.unshared(), actor)

    def prepared(self, environment: Environment, floor: BaseState, starter_environment_id: int, actor: Actor) -> Agent:
        return self.agents.save(Agent(environment_id=environment.row_id, role=AgentRole.MAIN, provider=self.provider(starter_environment_id), state=floor.name, data=floor.serialized(), stack=({"state": floor.name, "data": floor.serialized()},)), actor)

    def provider(self, environment_id: int) -> str:
        starter = self.agents.environment_main_agent(environment_id)
        return starter.provider if starter and starter.provider else self.providers.default().name

    def launched(self, environment: Environment, agent: Agent) -> None:
        resume = self.providers.lookup(agent.provider).resume(agent.session) if agent.session else ()
        self.launcher.start_in_worktree(environment.name, agent.provider, resume)

    def is_running(self, environment: Environment) -> bool:
        return self.supervisor.runs(environment.row_id)

    def stopped(self, environment: Environment) -> None:
        if self.is_running(environment):
            self.supervisor.stop(environment.row_id)
