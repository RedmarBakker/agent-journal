import sys
import threading
from contextlib import contextmanager
from pathlib import Path

from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.pending_uploads import PendingUploads
from journal.support.actor import Actor
from journal.sync.attachments import Attachments
from journal.sync.block_supply import BlockSupply
from journal.sync.host_desk import HostDesk
from journal.sync.incoming_changes import IncomingChanges
from journal.sync.journal_copy import JournalCopy
from journal.sync.pull_queries import PullQueries
from journal.sync.rejected_edits import RejectedEdits
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_change import TeamChange
from journal.sync.team_chat import TeamChat
from journal.sync.team_upgrade import TeamUpgrade
from sync_server.file_place import FilePlace
from sync_server.full_copy import FullCopy
from sync_server.pull_answer import PullAnswer
from sync_server.pull_query import PullQuery
from sync_server.sync_answer import SyncAnswer

# the longest one side of the sync waits for the other's lock before that is a fault
LOCK_SECONDS = 120


class SyncDesk:
    """The journal server's side of the team sync, which writes everything the sync brings and takes, so synced rows are written, cached and dispatched in the server alone: the query a pull asks with, the queue's next batch and the files waiting to go, a pull's answer applied past the sequence this journal holds with the host desk's requests, a push's result taking its batch off the queue and putting right the edits the server rejected, the team's full copy laid in, the Team chat lease and the row number blocks kept up, and the upgrade's finish. Its locks keep one answer applied at a time and nothing of this journal's going out while the team's copy is laid in."""

    def __init__(self, account: TeamAccount, outgoing: OutgoingChanges, incoming: IncomingChanges, rejected: RejectedEdits, status: SyncStatus, uploads: PendingUploads, attachments: Attachments, chat: TeamChat, upgrade: TeamUpgrade, copy: JournalCopy, supply: BlockSupply, queries: PullQueries, host: HostDesk) -> None:
        self.account, self.outgoing, self.incoming, self.rejected, self.status = account, outgoing, incoming, rejected, status
        self.uploads, self.attachments, self.chat, self.upgrade, self.copy = uploads, attachments, chat, upgrade, copy
        self.supply, self.queries, self.host = supply, queries, host
        self.applying, self.sending = threading.Lock(), threading.RLock()

    @staticmethod
    @contextmanager
    def held(lock, purpose: str):
        if not lock.acquire(timeout=LOCK_SECONDS):
            raise TimeoutError(f"the sync waited {LOCK_SECONDS} seconds to {purpose}, held by its other loop all that time")
        try:
            yield
        finally:
            lock.release()

    def query(self, wait_seconds: float) -> PullQuery:
        return self.queries.query(wait_seconds)

    def kept_up(self) -> None:
        self.chat.renew()
        self.refill()

    def refill(self) -> None:
        self.supply.refill()

    def batch(self, rows: int) -> list:
        return self.outgoing.sending_batch(rows)

    def waiting_files(self) -> list:
        return self.uploads.waiting()

    def file_place(self, upload) -> tuple[FilePlace, Path]:
        return FilePlace(upload.row_table, upload.row, upload.name), self.attachments.path(upload.row_table, upload.row, upload.name)

    def file_sent(self, upload) -> None:
        self.uploads.delete(upload, Actor.system())

    def pushed(self, batch: list, answer: SyncAnswer) -> int:
        self.outgoing.sent(batch)
        self.rejected.apply(answer.settlement.rejected)
        return self.answered(answer.delivery)

    def pushed_rows(self, ids: list[int], answer: SyncAnswer) -> int:
        return self.pushed(self.outgoing.sending_rows(ids), answer)

    def answered(self, answer: PullAnswer) -> int:
        count = self.applied(answer)
        self.host.handle(answer.requests)
        self.status.connected()
        return count

    def needs_copy(self, answer: PullAnswer) -> bool:
        return answer.copy_needed and self.account.sequence() < answer.head

    def applied(self, answer: PullAnswer) -> int:
        if self.needs_copy(answer):
            return 0
        with self.held(self.applying, "apply the team's changes"):
            sequence = self.account.sequence()
            changes = [TeamChange.logged(change) for change in answer.changes if change.sequence > sequence]
            self.incoming.apply(changes)
            self.account.record_pull(max(answer.head, sequence), answer.team_version)
            return len(changes)

    @contextmanager
    def laying_in(self):
        sys.stderr.write(f"the team asked for its full copy: this journal holds sequence {self.account.sequence()}\n")
        # nothing of this journal's goes out between the team's copy being taken and laid in place of its rows, or the copy would
        # wipe a change sent meanwhile, which no pull sends back, as a journal is never sent its own changes
        with self.held(self.sending, "lay in the team's copy"), self.held(self.applying, "lay in the team's copy"):
            yield

    def copied(self, copy: FullCopy) -> None:
        self.copy.replace(copy.rows, self.outgoing.rows())
        self.account.record_sequence(copy.head)

    def is_upgrader(self) -> bool:
        return self.account.is_upgrader()

    def upgrade_finished(self) -> None:
        self.upgrade.finish()

    def upgrade_claimed(self) -> None:
        self.upgrade.claim()

    def has_waiting(self) -> bool:
        return bool(self.outgoing.waiting())
