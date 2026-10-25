from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class BranchChanged(Event):
    """An agent's session switched to a branch, newly made or not."""

    environment_id: int
    session: str | None
    branch: str
