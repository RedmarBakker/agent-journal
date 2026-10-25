from dataclasses import dataclass
import re

from journal.events.rows.row_event import RowEvent

# the words in a task's title or brief that say it unblocks the agent that orchestrates: a permission it needs, access, a credential
UNBLOCKING = re.compile(r"\b(unblock(s|ing)?|permissions?|access|credentials?)\b", re.IGNORECASE)


@dataclass(frozen=True, kw_only=True)
class TaskDelegated(RowEvent):
    """A task was handed to a worker, which works it from now on, or put in a worker's queue; its title and brief, which may say it unblocks the orchestrator."""

    task_id: int
    title: str
    brief: str = ""

    def is_unblocking(self) -> bool:
        return bool(UNBLOCKING.search(f"{self.title}\n{self.brief}"))
