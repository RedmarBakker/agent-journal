from dataclasses import dataclass

from journal.events.rows.task_reopened import TaskReopened


@dataclass(frozen=True, kw_only=True)
class TaskReleased(TaskReopened):
    """A task delegated to a worker was given back open, as its worker let it go or its queue was drained; it was never blocked."""
