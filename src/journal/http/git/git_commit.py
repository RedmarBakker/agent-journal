from typing import TypedDict


class GitCommit(TypedDict):
    """A commit as the Git page lists it."""

    sha: str
    subject: str
    author: str
    time: float
