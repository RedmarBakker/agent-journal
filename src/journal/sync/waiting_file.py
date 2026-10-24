from dataclasses import dataclass

from sync_server.file_place import FilePlace


@dataclass(frozen=True)
class WaitingFile:
    """A file waiting to go to the team server: its row in the queue, where the team keeps it, and where it lies on this machine."""

    id: int
    place: FilePlace
    path: str
