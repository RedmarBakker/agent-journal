from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class GitPushed(Event):
    """A branch was pushed in an agent's session: the branch and the remote it went to."""

    environment_id: int
    session: str | None
    branch: str
    remote: str
