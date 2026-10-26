from typing import TypedDict


class GitBranch(TypedDict):
    """A branch as the Git page lists it: the commits it has beyond the base branch and those of the base it lacks, and its last commit."""

    name: str
    current: bool
    extra_commits: int
    missing_commits: int
    subject: str
    author: str
    time: float
