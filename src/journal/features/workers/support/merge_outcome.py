from dataclasses import dataclass

from journal.models.task import Task


@dataclass(frozen=True)
class MergeOutcome:
    """What a worker's merge resulted in: its task, closed, what happened to its worktree, and the next task of its queue it went on to."""

    task: Task
    worktree: str
    next_task: str = ""
