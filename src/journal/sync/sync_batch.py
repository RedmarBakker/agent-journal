from dataclasses import dataclass

from journal.sync.waiting_file import WaitingFile


@dataclass(frozen=True)
class SyncBatch:
    """What the sync desk hands the sync service to send: the queued changes by their rows, the files waiting, whether this journal booted as the team's upgrader, which finishes the upgrade before its first push, and the request body the team server takes the changes in."""

    ids: tuple[int, ...]
    files: tuple[WaitingFile, ...]
    upgrader: bool
    request_body: dict

    def is_empty(self) -> bool:
        return not self.ids and not self.files
