from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.stop import Stop
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_closed import TaskClosed
from journal.features.tasks.active_task import ActiveTask
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.agent import Agent
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.environments import Environments
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.agent_role import AgentRole
from journal.support.caller import Caller

FINISHED = ("completed", "cancelled")


class DefaultTaskAssigner:
    """The task assigner the idle floor names, the builder's and the solo agent's: at a stop, or when the main agent finishes the task it held, with no task in progress and auto mode on, it starts the agent's own paused task, those paused while it held them, else the first free open task by priority and then by number; never a blocked task, a task another agent or a worker holds, or a task of a plan not started."""

    def __init__(self, tasks: Tasks, active: ActiveTask, environments: Environments, settings: SettingRows) -> None:
        self.tasks, self.active, self.environments, self.settings = tasks, active, environments, settings

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent) -> Assignment:
        if agent.role != AgentRole.MAIN or not self.is_moment(agent, event) or not self.settings.option(TasksOptions.AUTO):
            return Assignment()
        if self.is_working(agent):
            return Assignment()
        task = self.picked(agent)
        if task is None:
            return Assignment()
        self.active.start(task, Caller.agent(self.environments.find(agent.environment_id).name, agent.session, agent.provider))
        return Assignment(task.row_id, task.title, "your own paused task" if task.state == TaskState.PAUSED else "the next open task in auto mode")

    def is_moment(self, agent: Agent, event: AgentEvent | RowEvent) -> bool:
        if isinstance(event, Stop):
            return event.session == agent.session
        return isinstance(event, TaskClosed) and event.outcome in FINISHED and self.tasks.holder(self.tasks.find(event.task_id)) == Ref.build(agent)

    def is_working(self, agent: Agent) -> bool:
        held = self.tasks.holder_task(Ref.build(agent))
        return held is not None and held.state == TaskState.STARTED

    def picked(self, agent: Agent) -> Task | None:
        holder = Ref.build(agent)
        own = [task for task in self.tasks.paused_tasks() if self.tasks.holder(task) == holder]
        return own[0] if own else self.tasks.next_open_task()
