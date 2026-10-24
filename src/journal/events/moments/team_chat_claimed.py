from dataclasses import dataclass

from journal.events.moments.sync_moment import SyncMoment


@dataclass(frozen=True, kw_only=True)
class TeamChatClaimed(SyncMoment):
    """Another person claimed the Team chat while its former holder was offline."""

    holder: str
    former: str
