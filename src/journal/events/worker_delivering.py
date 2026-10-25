from dataclasses import dataclass

from journal.events.worker_merging import WorkerMerging


@dataclass(frozen=True, kw_only=True)
class WorkerDelivering(WorkerMerging):
    """A worker's work is about to reach the agent that sent it: committed, rebased onto the project's branch and its tests passed; a plugin that holds it refuses the clock-out with its reason, for the worker to fix, test and clock out again."""
