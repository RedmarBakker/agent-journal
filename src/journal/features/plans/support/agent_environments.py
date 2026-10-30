from journal.engine.agent_launcher import AgentLauncher
from journal.engine.base_state import BaseState
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.supervisor_link import SupervisorLink


class AgentEnvironments:
    """An agent of its own in an environment of its own, for a plan or a task outside every plan: the environment records the kind of work and stable key of its source, and its agent is prepared on the work's floor, launched in its own worktree, and stopped."""

    def __init__(self, agents: Agents, environments: Environments, launcher: AgentLauncher, supervisor: SupervisorLink, providers: Providers, scope: Scope) -> None:
        self.agents, self.environments, self.launcher, self.supervisor, self.providers, self.scope = agents, environments, launcher, supervisor, providers, scope

    def made(self, name: str, source_environment_id: int, actor: Actor, generated_for: str | None = None) -> Environment:
        source = self.environments.find(source_environment_id)
        environment = self.environments.made(name, actor, source.key, generated_for or "")
        return self.visible(environment, source_environment_id, actor, generated_for)

    def visible(self, environment: Environment, source_environment_id: int, actor: Actor, generated_for: str | None = None) -> Environment:
        source = self.environments.find(source_environment_id)
        changes = {"parent_key": source.key}
        if generated_for is not None:
            changes["generated_for"] = generated_for
        if any(getattr(environment, name) != value for name, value in changes.items()):
            return self.environments.save(environment.with_(**changes), actor)
        return environment

    def prepared(self, environment: Environment, floor: BaseState, starter_environment_id: int, actor: Actor) -> Agent:
        with self.scope.environment(environment.row_id):
            return self.agents.save(Agent(environment_id=environment.row_id, role=AgentRole.MAIN, provider=self.provider(starter_environment_id), state=floor.name, data=floor.serialized(), stack=({"state": floor.name, "data": floor.serialized()},)), actor)

    def provider(self, environment_id: int) -> str:
        starter = self.agents.environment_main_agent(environment_id)
        return starter.provider if starter and starter.provider else self.providers.default().name

    def launched(self, environment: Environment, agent: Agent, repositories: tuple[str, ...] | None = None) -> None:
        resume = self.providers.lookup(agent.provider).resume(agent.session) if agent.session else ()
        self.launcher.start_in_worktree(environment.name, agent.provider, resume, repositories)

    def is_running(self, environment: Environment) -> bool:
        return self.supervisor.runs(environment.row_id)

    def stopped(self, environment: Environment) -> None:
        if self.is_running(environment):
            self.supervisor.stop(environment.row_id)
