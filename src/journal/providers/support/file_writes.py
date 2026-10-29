from dataclasses import dataclass

from journal.providers.support.peer_note import PeerNote


@dataclass(frozen=True)
class FileWrites:
    """What a transcript holds past where it was last read: the agent's text blocks, the messages other sessions sent it, and the byte after them."""

    texts: list[str]
    boundary_paths: list[PeerNote]
    time: int
