from dataclasses import dataclass
from typing import Self

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class WorkerMergeEvent(Event):
    """A moment of a worker's merge as plugins receive it: the worker by number and name, its task, its branch and worktree, and the environment it is in."""

    environment_id: int
    worker: int
    name: str
    task: int
    branch: str
    worktree: str

    def window(self, ceiling_ms: int) -> int:
        return ceiling_ms

    def with_window(self, window_ms: int) -> Self:
        return self
