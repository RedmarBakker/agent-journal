from dataclasses import dataclass, replace
from typing import Self

from journal.events.worker_merge_event import WorkerMergeEvent


@dataclass(frozen=True, kw_only=True)
class WorkerMerging(WorkerMergeEvent):
    """A worker's checked branch is about to be merged into base, with the inner repositories it has worktrees of, the files it changed and the milliseconds a plugin may hold it; a plugin that holds it refuses the merge with its reason."""

    repositories: tuple[str, ...]
    files: tuple[str, ...]
    base: str
    window_ms: int

    def window(self, ceiling_ms: int) -> int:
        return self.window_ms

    def with_window(self, window_ms: int) -> Self:
        return replace(self, window_ms=window_ms)
