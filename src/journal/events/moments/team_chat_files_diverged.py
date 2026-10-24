from dataclasses import dataclass

from journal.events.moments.sync_moment import SyncMoment


@dataclass(frozen=True, kw_only=True)
class TeamChatFilesDiverged(SyncMoment):
    """The Team chat's files on this machine have changes of their own, so they stay where they are and not at the holder's tip."""

    device: str
    local: str
    tip: str
