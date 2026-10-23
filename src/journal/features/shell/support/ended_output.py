from dataclasses import dataclass


@dataclass(frozen=True)
class EndedOutput:
    """A command that ended in the background, by its output's number, how it ended and what its reader picked from it."""

    id: int
    ending: str
    summary: str | None = None
