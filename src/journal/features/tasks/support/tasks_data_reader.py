from journal.engine.support.lazy_facts import LazyFacts
from journal.models.agent import Agent
from journal.models.open_task import OpenTask
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.task_logs import TaskLogs
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes

HISTORY_TOOL_STARTS = 6
POLL_COMMANDS = 3


class TasksDataReader:
    """Reads the tasks feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields TasksData names."""

    def __init__(self, tasks: Tasks, plans: Plans, entries: Entries, logs: TaskLogs, workers: Workers, scope: Scope, stages: StageTimes) -> None:
        self.tasks, self.plans, self.entries, self.logs, self.workers = tasks, plans, entries, logs, workers
        self.scope, self.stages = scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("tasks", {
            "current_task": lambda: self.current_id(agent),
            "last_log_line": lambda: self.current_log(agent),
            "paused": lambda: tuple(t.row_id for t in self.tasks.paused_tasks()),
            "pause_summary": lambda: ", ".join(f"task {task.id} ({task.title}), paused because: {task.pause_reason}" for task in self.tasks.paused_tasks()),
            "blocked": lambda: tuple(t.row_id for t in self.tasks.blocked_tasks()),
            "blocked_without_wait": lambda: tuple(t.row_id for t in self.tasks.blocked_without_wait()),
            "blocked_without_wait_summary": lambda: self.summary(self.tasks.blocked_without_wait()),
            "broken_waits": lambda: tuple(t.row_id for t, check in self.tasks.broken_waits()),
            "broken_waits_summary": lambda: "; ".join(f"task {task.id} waits on check {check.id}, {check.title}, which cannot run" for task, check in self.tasks.broken_waits()),
            "first_pause_reason": lambda: next((task.pause_reason for task in self.tasks.paused_tasks()), ""),
            "next_open": lambda: self.next_open(),
            "last_commands": lambda: self.last_commands(agent),
            "open_ids": lambda: tuple(t.row_id for t in self.tasks.open_tasks()),
            "open_summary": lambda: self.summary(self.tasks.open_tasks()),
            "started_ids": lambda: tuple(t.row_id for t in self.tasks.with_state(TaskState.STARTED)),
            "agent_tasks": lambda: self.tasks.holder_task_ids(self.workers.agent_holder(agent)),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def current_id(self, agent: Agent) -> int:
        current = self.tasks.current(agent)
        return current.row_id if current else 0

    def current_log(self, agent: Agent) -> str:
        current = self.tasks.current(agent)
        return self.last_log(current) if current else ""

    def next_open(self) -> OpenTask | None:
        free = self.plans.offers()
        return OpenTask(free[0].row_id, free[0].title, free[0].brief, 0) if free else None

    def last_commands(self, agent: Agent) -> tuple[str, ...]:
        commands = [command for e in self.entries.tool_starts(agent.session, HISTORY_TOOL_STARTS) if (command := e.recorded_call().command)]
        return tuple(commands[:POLL_COMMANDS])

    def last_log(self, task: Task) -> str:
        logs = self.logs.logs(task)
        return f'"{logs[-1].line}"' if logs else "nothing logged yet"

    @staticmethod
    def summary(tasks: list[Task]) -> str:
        return ", ".join(f"task {task.id} ({task.title})" for task in tasks)
