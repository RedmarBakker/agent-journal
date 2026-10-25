from dataclasses import dataclass

from journal.events.rows.worker_reused import WorkerReused


@dataclass(frozen=True, kw_only=True)
class WorkerSentOn(WorkerReused):
    """A worker whose work was just merged was sent the next task of its queue, which the merge's own mark says."""
