from journal.config import Config
from journal.events.rows.plan_abandoned import PlanAbandoned
from journal.events.rows.plan_finished import PlanFinished
from journal.events.rows.plan_postponed import PlanPostponed
from journal.events.rows.plan_started import PlanStarted
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.rig_seats import PLAN_AGENT, PLAN_POD
from journal.features.organization.support.usage_ledger import UsageLedger
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.agent import Agent, ENDED_STATE
from journal.models.author import Author
from journal.models.environment import Environment
from journal.models.message import Message
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.messages import Messages
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.missing_row import MissingRow
from journal.support.actor import Actor
from journal.support.inner_repositories import InnerRepositories
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class PlanAgents:
    """The one place that knows a plan's agent and its environment, plan-<n>, while Plan agents are on: a started plan is bound to that environment, which holds the agent its plan_agent link names, an agent row prepared on a LeadingPlan floor and launched in a worktree of the environment's name, on the provider of the main agent that started the plan, carrying on its last conversation, the environment made by whoever started the plan and seen as the plan's own environment is, shared with its team or private, set again at each start; a pause or an end stops it, and while they are off no plan is read, and environment, binding, row and link stay for its next start."""

    def __init__(self, config: Config, plans: Plans, agents: Agents, environments: Environments, bindings: PlanBindings, places: AgentEnvironments, settings: SettingRows, staffing: RigStaffing, usage: UsageLedger, time_source: TimeSource, scope: Scope, messages: Messages) -> None:
        self.config, self.inner_repositories = config, InnerRepositories(config.root)
        self.plans, self.agents, self.environments, self.bindings = plans, agents, environments, bindings
        self.places, self.settings, self.staffing = places, settings, staffing
        self.usage, self.time_source = usage, time_source
        self.scope = scope
        self.messages = messages

    def agent(self, plan: Plan) -> Agent | None:
        agent_id = self.plans.agent_id(plan)
        return next(iter(self.agents.global_matching(id=agent_id)), None) if agent_id else None

    def environment(self, plan: Plan) -> Environment | None:
        agent = self.agent(plan)
        return self.environments.find(agent.environment_id) if agent else None

    def led_plan(self, environment_id: int) -> Plan | None:
        return next((plan for plan in self.plans.global_matching(state=PlanState.STARTED) if (environment := self.environment(plan)) and environment.row_id == environment_id), None)

    def planned_task(self, task_id: int, agent_environment_id: int) -> Task:
        plan = self.led_plan(agent_environment_id)
        if plan is None:
            raise MissingRow(Task.table(), task_id)
        with self.scope.environment(plan.environment_id):
            task = next((task for task in self.plans.plan_tasks(plan) if task.row_id == task_id), None)
        if task is None:
            raise MissingRow(Task.table(), task_id)
        return task

    def is_running(self, environment: Environment) -> bool:
        plan = self.led_plan(environment.row_id)
        if plan and plan.mode == PlanMode.ORGANIZATION:
            agent = self.agent(plan)
            return bool(agent and self.staffing.is_running(plan, agent.provider))
        return self.places.is_running(environment)

    def is_on(self) -> bool:
        return bool(self.settings.option(PlansOptions.PLAN_AGENTS))

    def started(self, event: PlanStarted) -> None:
        with self.scope.environment(event.environment_id):
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
                try:
                    self.staffing.start_plan(plan, environment, agent, actor)
                except Rejection as reason:
                    self.messages.save(Message(
                        environment_id=event.environment_id,
                        author=Author.SYSTEM,
                        text=f"Plan {plan.id} needs OpenRig attention: {reason}",
                        data={"kind": "plan_attention", "plan": plan.id},
                    ), Actor.system())
            else:
                self.places.launched(environment, agent, self.repository_folders(plan))

    def prepared(self, plan: Plan, environment: Environment, starter_environment_id: int, actor: Actor) -> Agent:
        from journal.features.plans.states.leading_plan import LeadingPlan

        agent = self.places.prepared(environment, LeadingPlan(plan_id=plan.row_id), starter_environment_id, actor)
        self.plans.agent_linked(plan, agent, actor)
        return agent

    def stopped(self, event: PlanAbandoned | PlanFinished | PlanPostponed) -> None:
        with self.scope.environment(event.environment_id):
            if not self.is_on():
                return
            plan = self.plans.find(event.plan_id)
            if plan.mode in (PlanMode.SOLO, PlanMode.ORGANIZATION):
                self.record_usage(plan)
            environment = self.environment(plan)
            if environment:
                if agent := self.agent(plan):
                    with self.scope.environment(agent.environment_id):
                        current = self.agents.find(agent.row_id)
                        if current.state != ENDED_STATE:
                            stopped = (
                                current.plan_stopped(plan.row_id, event.time)
                                if plan.state.is_closed()
                                else current.retired(event.time)
                            )
                            self.agents.save(stopped, Actor.system())
                if plan.mode == PlanMode.ORGANIZATION:
                    if agent:
                        self.staffing.stop_plan(plan, agent.provider)
                self.places.stopped(environment)

    def repository_folders(self, plan: Plan) -> tuple[str, ...]:
        tasks = self.plans.plan_tasks(plan)
        brief = " ".join((plan.brief, *(f"{task.title} {task.brief}" for task in tasks)))
        return self.inner_repositories.named_in(brief) or self.inner_repositories.names()

    def record_usage(self, plan: Plan) -> None:
        agent = self.agent(plan)
        if not agent:
            return
        if plan.mode == PlanMode.ORGANIZATION:
            rig_id = self.plans.rig_id(plan)
            if not rig_id:
                return
            rig = self.staffing.find_rig(rig_id)
            target = self.staffing.runtime.target(rig.name, PLAN_POD, PLAN_AGENT)
            reading = self.staffing.runtime.usage_cost(target)
            self.usage.record(plan.id, target, reading.native_session_id or target, reading,
                              self.time_source.seconds(), self.staffing.runtime.expected_seats(rig.name))
            return
        if not agent.session:
            return
        provider = self.places.providers.lookup(agent.provider)
        amount = provider.estimated_cost(agent.session, self.config.status_home)
        if amount is not None:
            self.usage.record_session_estimate(plan.id, f"plan-agent-{agent.id}", agent.session, amount, self.time_source.seconds(), f"{provider.title} status line")
