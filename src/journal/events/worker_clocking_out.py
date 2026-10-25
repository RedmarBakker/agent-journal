from dataclasses import dataclass

from journal.events.worker_merging import WorkerMerging


@dataclass(frozen=True, kw_only=True)
class WorkerClockingOut(WorkerMerging):
    """A worker is clocking out: the journal committed its changes and has not yet rebased them, so a plugin judges the worker's own commit; a plugin that holds it refuses the clock-out with its reason, for the worker to fix in its own session."""
