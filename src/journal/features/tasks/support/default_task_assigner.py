from dataclasses import replace

from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.stop import Stop
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_closed import TaskClosed
from journal.features.tasks.active_task import ActiveTask
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.tasks.support.ready_queue import ReadyQueue
from journal.models.agent import Agent
from journal.models.open_task import OpenTask
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.environments import Environments
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.caller import Caller

FINISHED = ("completed", "cancelled", "testing")


class DefaultTaskAssigner:
    """The task assigner the idle floor names: at a stop, or when the main agent finishes the task it held, with no task in progress and auto mode on, it starts the first free open task by priority and then by number, a blocked task among them as soon as its block ends; never a blocked task, a task another agent or a worker holds, or a task of a plan not started. Its queries name, without starting it, the task it would take next and, in auto mode, the blocked and open work the lines tell of, so auto mode is read here alone."""

    def __init__(self, tasks: Tasks, active: ActiveTask, environments: Environments,
                 settings: SettingRows, ready: ReadyQueue) -> None:
        self.tasks, self.active, self.environments, self.settings, self.ready = tasks, active, environments, settings, ready

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent, quantity: int = 1) -> Assignment:
        if not self.is_free_moment(agent, event):
            return Assignment()
        return self.with_following(self.started(agent, self.free_task()), quantity)

    def with_following(self, assignment: Assignment, quantity: int) -> Assignment:
        if quantity <= 1 or not assignment.has_task():
            return assignment
        return replace(assignment, following_ids=tuple(task.row_id for task in self.free_tasks(quantity) if task.row_id != assignment.task_id)[:quantity - 1])

    def free_tasks(self, count: int) -> list[Task]:
        return self.ready.open_tasks(count + 1) if self.is_auto() else []

    def is_free_moment(self, agent: Agent, event: AgentEvent | RowEvent) -> bool:
        return agent.is_main() and self.is_moment(agent, event) and not self.is_working(agent)

    def is_moment(self, agent: Agent, event: AgentEvent | RowEvent) -> bool:
        if isinstance(event, Stop):
            return event.session == agent.session
        return isinstance(event, TaskClosed) and event.outcome in FINISHED and self.tasks.task_holder(event.task_id) == Ref.build(agent)

    def is_working(self, agent: Agent) -> bool:
        current = self.tasks.holder_task(Ref.build(agent))
        return current is not None and current.is_started()

    def free_task(self) -> Task | None:
        return self.ready.open_task() if self.is_auto() else None

    def offered(self, agent: Agent) -> OpenTask | None:
        return self.open_task(self.free_task())

    def open_work(self, agent: Agent) -> OpenTask | None:
        return self.open_task(self.ready.open_task())

    @staticmethod
    def open_task(task: Task | None) -> OpenTask | None:
        return OpenTask(task.row_id, task.title, task.brief, 0, task.state.value) if task is not None else None

    def is_auto(self) -> bool:
        return bool(self.settings.option(TasksOptions.AUTO))

    def blocked_work(self) -> list[Task]:
        return self.tasks.blocked_tasks() if self.is_auto() else []

    def open_ids(self, count: int) -> tuple[int, ...]:
        return self.ready.open_ids(count) if self.is_auto() else ()

    def started(self, agent: Agent, task: Task | None) -> Assignment:
        if task is None:
            return Assignment()
        self.active.start(task, Caller.agent(self.environments.find(agent.environment_id).name, agent.session, agent.provider))
        return Assignment(task.row_id, task.title, "the next open task in auto mode")
