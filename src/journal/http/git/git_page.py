from typing import TypedDict


class GitPage(TypedDict):
    """A page of a list the Git page reads: its rows and whether it is the last."""

    rows: list
    is_last_page: bool
