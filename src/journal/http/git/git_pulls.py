from typing import TypedDict

from journal.http.git.git_pull import GitPull


class GitPulls(TypedDict):
    """The open pull requests as the Git page reads them, and whether gh was there to list them."""

    available: bool
    rows: list[GitPull]
