from dataclasses import dataclass

from journal.sync.waiting_file import WaitingFile


@dataclass(frozen=True)
class SyncBatch:
    """What the sync desk hands its carrier to send: the queued changes by their rows and as the team server takes them, the files waiting, and whether this journal booted as the team's upgrader, which finishes the upgrade before its first push."""

    ids: tuple[int, ...]
    changes: tuple[dict, ...]
    files: tuple[WaitingFile, ...]
    upgrader: bool

    def is_empty(self) -> bool:
        return not self.ids and not self.files
