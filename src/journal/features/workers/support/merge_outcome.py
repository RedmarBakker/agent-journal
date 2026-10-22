from dataclasses import dataclass

from journal.models.task import Task


@dataclass(frozen=True)
class MergeOutcome:
    """What a worker's merge resulted in: its task, closed, and what happened to its worktree."""

    task: Task
    worktree: str
