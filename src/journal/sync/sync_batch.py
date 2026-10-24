from dataclasses import dataclass, field

from journal.sync.waiting_file import WaitingFile


@dataclass(frozen=True)
class SyncBatch:
    """What the sync desk hands its carrier to send: the queued changes by their rows and as the team server takes them, the files waiting, whether this journal booted as the team's upgrader, which finishes the upgrade before its first push, and the push the team server takes them in."""

    ids: tuple[int, ...]
    changes: tuple[dict, ...]
    files: tuple[WaitingFile, ...]
    upgrader: bool
    push: dict = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not self.ids and not self.files
