from journal.engine.agent_launcher import AgentLauncher
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.supervisor_link import SupervisorLink


class PlanAgents:
    """The one place that knows a plan's agent and its environment, plan-<n>, while Plan agents are on: a started plan is bound to that environment, which holds the agent its plan_agent link names, an agent row prepared on a LeadingPlan floor and launched in a worktree of the environment's name, on the provider of the main agent that started the plan, carrying on its last conversation; a pause or an end stops it, and while they are off no plan is read, and environment, binding, row and link stay for its next start."""

    def __init__(self, plans: Plans, agents: Agents, environments: Environments, bindings: PlanBindings, launcher: AgentLauncher, supervisor: SupervisorLink, settings: SettingRows, providers: Providers) -> None:
        self.plans, self.agents, self.environments, self.bindings = plans, agents, environments, bindings
        self.launcher, self.supervisor, self.settings, self.providers = launcher, supervisor, settings, providers

    def agent(self, plan: Plan) -> Agent | None:
        agent_id = self.plans.agent_id(plan)
        return self.agents.find(agent_id) if agent_id else None

    def environment(self, plan: Plan) -> Environment | None:
        agent = self.agent(plan)
        return self.environments.find(agent.environment_id) if agent else None

    def is_running(self, environment: Environment) -> bool:
        return self.supervisor.runs(environment.row_id)

    def is_on(self) -> bool:
        return bool(self.settings.option(PlansOptions.PLAN_AGENTS))

    def started(self, plan_id: int, starter_environment_id: int, actor: Actor) -> None:
        if not self.is_on():
            return
        plan = self.plans.find(plan_id)
        environment = self.environment(plan) or self.environments.lookup(f"plan-{plan.id}")
        if self.is_running(environment):
            return
        self.bindings.bind(plan, environment.row_id, actor)
        agent = self.agent(plan) or self.prepared(plan, environment, self.provider(starter_environment_id), actor)
        resume = self.providers.lookup(agent.provider).resume(agent.session) if agent.session else ()
        self.launcher.start_in_worktree(environment.name, agent.provider, resume)

    def prepared(self, plan: Plan, environment: Environment, provider: str, actor: Actor) -> Agent:
        floor = LeadingPlan(plan_id=plan.row_id)
        agent = self.agents.save(Agent(environment_id=environment.row_id, role=AgentRole.MAIN, provider=provider, state=floor.name, data=floor.serialized(), stack=({"state": floor.name, "data": floor.serialized()},)), actor)
        self.plans.agent_linked(plan, agent, actor)
        return agent

    def provider(self, environment_id: int) -> str:
        starter = self.agents.environment_main_agent(environment_id)
        return starter.provider if starter and starter.provider else self.providers.default().name

    def stopped(self, plan_id: int) -> None:
        if not self.is_on():
            return
        environment = self.environment(self.plans.find(plan_id))
        if environment and self.is_running(environment):
            self.supervisor.stop(environment.row_id)
