from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerRebased(RowEvent):
    """The journal rebased a worker's worktree onto the project's branch on the agent's order: where it stands now, or the files that clash."""

    worker: WorkerMention
    outcome: str
