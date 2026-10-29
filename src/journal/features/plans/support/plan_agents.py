from journal.events.rows.plan_started import PlanStarted
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor


class PlanAgents:
    """The one place that knows a plan's agent and its environment, plan-<n>, while Plan agents are on: a started plan is bound to that environment, which holds the agent its plan_agent link names, an agent row prepared on a LeadingPlan floor and launched in a worktree of the environment's name, on the provider of the main agent that started the plan, carrying on its last conversation, the environment made by whoever started the plan and seen as the plan's own environment is, shared with its team or private, set again at each start; a pause or an end stops it, and while they are off no plan is read, and environment, binding, row and link stay for its next start."""

    def __init__(self, plans: Plans, agents: Agents, environments: Environments, bindings: PlanBindings, places: AgentEnvironments, settings: SettingRows) -> None:
        self.plans, self.agents, self.environments, self.bindings = plans, agents, environments, bindings
        self.places, self.settings = places, settings

    def agent(self, plan: Plan) -> Agent | None:
        agent_id = self.plans.agent_id(plan)
        return self.agents.find(agent_id) if agent_id else None

    def environment(self, plan: Plan) -> Environment | None:
        agent = self.agent(plan)
        return self.environments.find(agent.environment_id) if agent else None

    def led_plan(self, environment_id: int) -> Plan | None:
        return next((plan for plan in self.plans.running_plans() if (environment := self.environment(plan)) and environment.row_id == environment_id), None)

    def is_running(self, environment: Environment) -> bool:
        return self.places.is_running(environment)

    def is_on(self) -> bool:
        return bool(self.settings.option(PlansOptions.PLAN_AGENTS))

    def started(self, event: PlanStarted) -> None:
        if not self.is_on():
            return
        plan, actor = self.plans.find(event.plan_id), Actor.parse(event.actor)
        environment = self.environment(plan)
        environment = self.places.visible(environment, plan.environment_id, actor) if environment else self.places.made(f"plan-{plan.id}", plan.environment_id, actor)
        if self.is_running(environment):
            return
        self.bindings.bind(plan, environment.row_id, actor)
        agent = self.agent(plan) or self.prepared(plan, environment, event.environment_id, actor)
        self.places.launched(environment, agent)

    def prepared(self, plan: Plan, environment: Environment, starter_environment_id: int, actor: Actor) -> Agent:
        agent = self.places.prepared(environment, LeadingPlan(plan_id=plan.row_id), starter_environment_id, actor)
        self.plans.agent_linked(plan, agent, actor)
        return agent

    def stopped(self, plan_id: int) -> None:
        if not self.is_on():
            return
        environment = self.environment(self.plans.find(plan_id))
        if environment:
            self.places.stopped(environment)
