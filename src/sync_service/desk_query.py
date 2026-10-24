from dataclasses import dataclass


@dataclass(frozen=True)
class DeskQuery:
    """The pull the journal server asks the sync service to make of the team server: its path, and how long the team server may hold it."""

    path: str
    wait_seconds: float
