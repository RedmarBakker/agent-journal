from typing import TypedDict


class GitPull(TypedDict):
    """An open pull request as the Git page lists it, with its checks and its review state."""

    number: int
    title: str
    branch: str
    author: str
    draft: bool
    review: str
    checks_passed: int
    checks_failed: int
    checks_pending: int
    url: str
