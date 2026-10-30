from typing import TypedDict


class Counts(TypedDict):
    """How many rows of a resource there are, how many are open, and how many of those the user has not seen; for plans, how many are being worked, which the sidebar shows."""

    all: int
    open: int
    unread: int
