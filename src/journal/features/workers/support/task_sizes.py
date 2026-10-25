from journal.features.workers.workers_options import WorkersOptions
from journal.models.task import Task
from journal.repositories.setting_rows import SettingRows


class TaskSizes:
    """How big the work given to a worker is, defined once: a task is small or large by the points of its brief, and a queue is long by its count of tasks, each by the user's numbers; the report choice's suggestion and its misfit drop both read it."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def is_small(self, task: Task) -> bool:
        return len(task.points()) <= self.settings.integer(WorkersOptions.SMALL_TASK_POINTS)

    def is_large(self, task: Task) -> bool:
        return len(task.points()) >= self.settings.integer(WorkersOptions.LARGE_TASK_POINTS)

    def is_long(self, tasks: list[Task]) -> bool:
        return len(tasks) >= self.settings.integer(WorkersOptions.LONG_QUEUE_TASKS)
