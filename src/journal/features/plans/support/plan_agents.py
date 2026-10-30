from journal.config import Config
from journal.events.rows.plan_started import PlanStarted
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.usage_ledger import UsageLedger
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.inner_repositories import InnerRepositories
from journal.support.time_source import TimeSource


class PlanAgents:
    """The one place that knows a plan's agent and its environment, plan-<n>, while Plan agents are on: a started plan is bound to that environment, which holds the agent its plan_agent link names, an agent row prepared on a LeadingPlan floor and launched in a worktree of the environment's name, on the provider of the main agent that started the plan, carrying on its last conversation, the environment made by whoever started the plan and seen as the plan's own environment is, shared with its team or private, set again at each start; a pause or an end stops it, and while they are off no plan is read, and environment, binding, row and link stay for its next start."""

    def __init__(self, config: Config, plans: Plans, agents: Agents, environments: Environments, bindings: PlanBindings, places: AgentEnvironments, settings: SettingRows, staffing: RigStaffing, usage: UsageLedger, time_source: TimeSource) -> None:
        self.config, self.inner_repositories = config, InnerRepositories(config.root)
        self.plans, self.agents, self.environments, self.bindings = plans, agents, environments, bindings
        self.places, self.settings, self.staffing = places, settings, staffing
        self.usage, self.time_source = usage, time_source

    def agent(self, plan: Plan) -> Agent | None:
        agent_id = self.plans.agent_id(plan)
        return self.agents.find(agent_id) if agent_id else None

    def environment(self, plan: Plan) -> Environment | None:
        agent = self.agent(plan)
        return self.environments.find(agent.environment_id) if agent else None

    def led_plan(self, environment_id: int) -> Plan | None:
        return next((plan for plan in self.plans.running_plans() if (environment := self.environment(plan)) and environment.row_id == environment_id), None)

    def is_running(self, environment: Environment) -> bool:
        plan = self.led_plan(environment.row_id)
        if plan and plan.mode == PlanMode.ORGANIZATION:
            agent = self.agent(plan)
            return bool(agent and self.staffing.is_running(plan, agent.provider))
        return self.places.is_running(environment)

    def is_on(self) -> bool:
        return bool(self.settings.option(PlansOptions.PLAN_AGENTS))

    def started(self, event: PlanStarted) -> None:
        if not self.is_on():
            return
        plan, actor = self.plans.find(event.plan_id), Actor.parse(event.actor)
        environment = self.environment(plan)
        environment = self.places.visible(environment, plan.environment_id, actor, "plan") if environment else self.places.made(f"plan-{plan.id}", plan.environment_id, actor, "plan")
        agent = self.agent(plan)
        if plan.mode == PlanMode.ORGANIZATION:
            if agent and self.staffing.is_running(plan, agent.provider):
                return
        elif self.places.is_running(environment):
            return
        self.bindings.bind(plan, environment.row_id, actor)
        agent = agent or self.prepared(plan, environment, event.environment_id, actor)
        if plan.mode == PlanMode.ORGANIZATION:
            self.staffing.start_plan(plan, environment, agent, actor)
        else:
            self.places.launched(environment, agent, self.repository_folders(plan))

    def prepared(self, plan: Plan, environment: Environment, starter_environment_id: int, actor: Actor) -> Agent:
        agent = self.places.prepared(environment, LeadingPlan(plan_id=plan.row_id), starter_environment_id, actor)
        self.plans.agent_linked(plan, agent, actor)
        return agent

    def stopped(self, plan_id: int) -> None:
        if not self.is_on():
            return
        plan = self.plans.find(plan_id)
        if plan.mode == PlanMode.SOLO:
            self.record_usage(plan)
        environment = self.environment(plan)
        if environment:
            if plan.mode == PlanMode.ORGANIZATION:
                agent = self.agent(plan)
                if agent:
                    self.staffing.stop_plan(plan, agent.provider)
            self.places.stopped(environment)

    def repository_folders(self, plan: Plan) -> tuple[str, ...]:
        tasks = self.plans.plan_tasks(plan)
        brief = " ".join((plan.brief, *(f"{task.title} {task.brief}" for task in tasks)))
        return self.inner_repositories.named_in(brief) or self.inner_repositories.names()

    def record_usage(self, plan: Plan) -> None:
        agent = self.agent(plan)
        if not agent or not agent.session:
            return
        provider = self.places.providers.lookup(agent.provider)
        amount = provider.estimated_cost(agent.session, self.config.status_home)
        if amount is not None:
            self.usage.record_session_estimate(plan.id, f"plan-agent-{agent.id}", agent.session, amount, self.time_source.seconds(), f"{provider.title} status line")
