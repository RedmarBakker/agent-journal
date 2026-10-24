from typing import Protocol, runtime_checkable

from journal.sync.desk_answer import DeskAnswer
from journal.sync.sync_batch import SyncBatch
from sync_server.full_copy import FullCopy
from sync_server.pull_answer import PullAnswer
from sync_server.pull_query import PullQuery
from sync_server.sync_answer import SyncAnswer


@runtime_checkable
class DeskDoors(Protocol):
    """How the sync's carrier reaches the sync desk, which writes everything sync brings: in the journal server's own process, or over its local doors from a process of its own."""

    def query(self, wait_seconds: float) -> PullQuery: ...

    def batch(self, wait_seconds: float) -> SyncBatch: ...

    def files_sent(self, ids: tuple[int, ...]) -> None: ...

    def pushed(self, batch: SyncBatch, answer: SyncAnswer) -> DeskAnswer: ...

    def answered(self, answer: PullAnswer) -> DeskAnswer: ...

    def copied(self, copy: FullCopy) -> bool: ...

    def upgrade_claimed(self) -> None: ...

    def upgrade_finished(self) -> None: ...

    def wake(self) -> None: ...
