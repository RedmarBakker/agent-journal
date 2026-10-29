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
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor

TASK_AGENT_LINK = "task_agent"


class TaskAgents:
    """The one place that knows the agent of a task outside every plan while Plan agents are on: the main agent's start of such a task hands it to an agent of its own in the task's environment task-<n>, as a one-task solo plan's, with no plan row made: the task bound to that environment and held by the agent its task_agent link names, prepared on a LeadingTask floor; the task's close stops it. A task started in a Plan agent's or a task agent's own environment is that agent's own work, never handed on."""

    def __init__(self, tasks: Tasks, agents: Agents, environments: Environments, links: Links, bindings: PlanBindings, places: AgentEnvironments, plan_agents: PlanAgents, settings: SettingRows) -> None:
        self.tasks, self.agents, self.environments, self.links, self.bindings = tasks, agents, environments, links, bindings
        self.places, self.plan_agents, self.settings = places, plan_agents, settings

    def agent(self, task: Task) -> Agent | None:
        agent_id = self.links.target_id(task, TASK_AGENT_LINK)
        return self.agents.find(agent_id) if agent_id else None

    def environment(self, task: Task) -> Environment | None:
        agent = self.agent(task)
        return self.environments.find(agent.environment_id) if agent else None

    def is_own_work(self, environment_id: int) -> bool:
        return self.plan_agents.led_plan(environment_id) is not None or any(self.links.sources(agent, TASK_AGENT_LINK) for agent in self.agents.main_scoped(environment_id))

    def started(self, event: TaskStarted) -> None:
        if event.plan_id or not self.settings.option(PlansOptions.PLAN_AGENTS) or self.is_own_work(event.environment_id):
            return
        task, actor = self.tasks.find(event.task_id), Actor.parse(event.actor)
        environment = self.environment(task)
        environment = self.places.visible(environment, task.environment_id, actor) if environment else self.places.made(f"task-{task.id}", task.environment_id, actor)
        if self.places.is_running(environment):
            return
        self.bindings.bind(task, environment.row_id, actor)
        agent = self.agent(task) or self.prepared(task, environment, event.environment_id, actor)
        self.tasks.handover(task, Ref.build(agent), actor)
        self.places.launched(environment, agent)

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
