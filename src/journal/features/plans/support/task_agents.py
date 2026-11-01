from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_started import TaskStarted
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.leading_task import LeadingTask
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.missing_row import MissingRow

TASK_AGENT_LINK = "task_agent"


class TaskAgents:
    """The one place that starts an agent for a task outside every plan and lets that agent read only its linked task in its task environment."""

    def __init__(
        self, tasks: Tasks, agents: Agents, environments: Environments, links: Links,
        bindings: PlanBindings, places: AgentEnvironments, plan_agents: PlanAgents,
        plans: Plans, scope: Scope, settings: SettingRows,
    ) -> None:
        self.tasks, self.agents, self.environments, self.links, self.bindings = tasks, agents, environments, links, bindings
        self.places, self.plan_agents, self.plans, self.scope, self.settings = places, plan_agents, plans, scope, settings

    def agent(self, task: Task) -> Agent | None:
        agent_id = next((target.id for target in self.links.targets(task, TASK_AGENT_LINK)), 0)
        return next(iter(self.agents.global_matching(id=agent_id)), None) if agent_id else None

    def environment(self, task: Task) -> Environment | None:
        agent = self.agent(task)
        return self.environments.find(agent.environment_id) if agent else None

    def is_own_work(self, environment_id: int) -> bool:
        return self.plan_agents.led_plan(environment_id) is not None or any(self.links.sources(agent, TASK_AGENT_LINK) for agent in self.agents.main_scoped(environment_id))

    def started(self, event: TaskStarted) -> None:
        if not self.settings.option(PlansOptions.PLAN_AGENTS) or self.is_own_work(event.environment_id):
            return
        task, actor = self.tasks.find(event.task_id), Actor.parse(event.actor)
        if event.plan_id or self.plans.containing(task):
            return
        environment = self.environment(task)
        environment = self.places.visible(environment, task.environment_id, actor, "task") if environment else self.places.made(f"task-{task.id}", task.environment_id, actor, "task")
        if self.places.is_running(environment):
            return
        self.bindings.bind(task, environment.row_id, actor)
        agent = self.agent(task) or self.prepared(task, environment, event.environment_id, actor)
        self.tasks.handover(task, Ref.build(agent), actor)
        self.places.launched(environment, agent)

    def task_for_environment(self, task_id: int, environment_id: int) -> Task:
        task = next(iter(self.tasks.global_matching(id=task_id)), None)
        if task is not None:
            with self.scope.environment(task.environment_id):
                agent = self.agent(task)
            if agent and agent.environment_id == environment_id:
                return task
        raise MissingRow(Task.table(), task_id)

    def prepared(self, task: Task, environment: Environment, starter_environment_id: int, actor: Actor) -> Agent:
        agent = self.places.prepared(environment, LeadingTask(task_id=task.row_id), starter_environment_id, actor)
        self.links.linked(Ref.build(task), Ref.build(agent), TASK_AGENT_LINK, actor)
        return agent

    def stopped(self, event: TaskClosed) -> None:
        if not self.settings.option(PlansOptions.PLAN_AGENTS):
            return
        environment = self.environment(self.tasks.find(event.task_id))
        if environment:
            self.places.stopped(environment)
