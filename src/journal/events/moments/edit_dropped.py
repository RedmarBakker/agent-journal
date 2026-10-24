from dataclasses import dataclass

from journal.events.moments.sync_moment import SyncMoment


@dataclass(frozen=True, kw_only=True)
class EditDropped(SyncMoment):
    """A row was deleted by a colleague, so this machine's edit of it was dropped."""

    noun: str
    row_id: int
