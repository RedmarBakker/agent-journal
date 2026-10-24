from dataclasses import dataclass

from sync_service.desk_file import DeskFile


@dataclass(frozen=True)
class DeskBatch:
    """What the journal server hands the sync service to send: the queued changes by their rows, the files waiting, whether this journal booted as the team's upgrader, and the request body the team server takes the changes in, which the service sends as it is."""

    ids: tuple[int, ...]
    files: tuple[DeskFile, ...]
    upgrader: bool
    request_body: dict

    @classmethod
    def parsed(cls, ids: list, files: list, upgrader: bool, request_body: dict) -> "DeskBatch":
        return cls(tuple(ids), tuple(DeskFile(file["id"], file["path"], file["address"]) for file in files), upgrader, request_body)
