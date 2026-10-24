from dataclasses import dataclass


@dataclass(frozen=True)
class DeskFile:
    """A file the journal server hands the sync service to send first: its row in the queue, where it lies on this machine, and its address on the team server."""

    id: int
    path: str
    address: str
