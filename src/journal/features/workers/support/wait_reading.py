import re

from journal.features.tasks.support.person_wait import PersonWait
from journal.features.workers.workers_options import WorkersOptions
from journal.models.support.ref import Ref
from journal.models.support.wait_use import WaitUse
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.task_logs import TaskLogs
from journal.repositories.tasks import Tasks

# another task a brief or a log line names: task 12, after 12, once 12 is done
TASK_NAMED = re.compile(r"\b(?:task|after|once)\s+#?(\d+)\b(?!\s*(?:min|minutes?|hours?|seconds?|days?|%))", re.IGNORECASE)
HELD = (TaskState.BLOCKED, TaskState.PAUSED)


class WaitReading:
    """Reads how the tasks of the started plans wait: each blocked or paused one by whether it waits with --on or --until, or only in words, and whether those words name the user or an outside party; each open one whose brief or log names another open task it does not wait on; and each started plan with many open tasks and none blocked."""

    def __init__(self, plans: Plans, tasks: Tasks, logs: TaskLogs, settings: SettingRows, people: PersonWait) -> None:
        self.plans, self.tasks, self.logs, self.settings, self.people = plans, tasks, logs, settings, people

    def measured(self) -> WaitUse:
        plans = self.plans.running_plans()
        unclosed = [task for plan in plans for task in self.plans.plan_tasks(plan) if not task.is_closed()]
        held = [task for task in unclosed if task.state in HELD]
        waiting = [task for task in held if self.tasks.open_waits(task)]
        worded = [task for task in held if task not in waiting]
        outside = sum(1 for task in worded if self.people.names_someone_outside(task.waiting_reason()))
        least = self.settings.integer(WorkersOptions.UNORDERED_PLAN_TASKS)
        unordered = sum(1 for plan in plans if least and self.plans.remaining_count(plan) >= least and not self.plans.blocked_count(plan))
        return WaitUse(len(waiting), len(worded) - outside, outside, self.missing(unclosed), unordered)

    def missing(self, unclosed: list[Task]) -> tuple[str, ...]:
        ids = {task.row_id for task in unclosed}
        return tuple(f"{task.row_id}:{other}" for task in unclosed for other in self.named(task) if other in ids and other != task.row_id and Ref(Task.table(), other) not in self.tasks.open_waits(task))

    def named(self, task: Task) -> list[int]:
        text = "\n".join((task.brief, *(log.line for log in self.logs.logs(task))))
        return list(dict.fromkeys(int(match[1]) for match in TASK_NAMED.finditer(text)))
