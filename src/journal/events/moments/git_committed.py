from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class GitCommitted(Event):
    """A commit was made in an agent's session: the commit's sha, the branch it is on, its subject, how many files it changed, and the lines it added per path."""

    environment_id: int
    session: str | None
    sha: str
    branch: str
    subject: str
    files: int
    lines: tuple[tuple[str, int], ...] = ()
