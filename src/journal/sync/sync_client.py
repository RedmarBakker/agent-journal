import threading
import time
from typing import Callable

from journal.sync.attachments import Attachments
from journal.repositories.pending_uploads import PendingUploads
from journal.support.actor import Actor
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.sync.commit_signal import CommitSignal
from journal.sync.incoming_changes import IncomingChanges
from journal.sync.journal_copy import JournalCopy
from journal.sync.rejected_edits import RejectedEdits
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_change import TeamChange
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink
from sync_server.file_place import FilePlace
from journal.sync.team_chat import TeamChat
from journal.sync.team_upgrade import TeamUpgrade
from journal.sync.block_supply import BlockSupply
from journal.sync.host_desk import HostDesk
from journal.sync.hosts import Hosts
from sync_server.pull_answer import PullAnswer

BATCH_ROWS = 200
IDLE_SECONDS = 5
LONG_POLL_SECONDS = 25
FIRST_RETRY_SECONDS = 1
LAST_RETRY_SECONDS = 30


class SyncClient:
    """Keeps a joined journal in step with its team: a send loop pushes the queued changes oldest first in batches, woken by every commit that queues one, and a receive loop long-polls for the team's changes and applies them. On a fault both wait 1, 2, 4 seconds and so on up to 30 and try again; a change is removed from the queue only once the server answered for it, and the edits it rejected are put right here; once it has taken a batch it sends every file attached here that the server lacks, before the batch, so no change in it names a file the server has not got, renews the Team chat's lease while this machine holds it, and asks for a block of row numbers for every shared table that holds less than a block and a fifth. Every push carries a pull, so its answer brings the team's changes as the long poll does, and both bring the writes waiting for the environments this journal hosts, which its host desk makes; changes are applied one answer at a time and only past the sequence this journal holds, so the two loops never apply one twice. The clock offset is measured from the server's time in each pull answer and sent with each push. Before an upgrade it takes the team's upgrade lease, sends its whole queue and pulls to the server's head; a journal that booted as the upgrader finishes the upgrade before its loops start, and one behind another's upgrade takes the team's copy in place of its shared rows."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, outgoing: OutgoingChanges, incoming: IncomingChanges, rejected: RejectedEdits, signal: CommitSignal, status: SyncStatus, uploads: PendingUploads, attachments: Attachments, chat: TeamChat, upgrade: TeamUpgrade, copy: JournalCopy, supply: BlockSupply, hosts: Hosts, desk: HostDesk) -> None:
        self.account, self.link, self.outgoing, self.incoming, self.rejected, self.signal, self.status = account, link, outgoing, incoming, rejected, signal, status
        self.uploads, self.attachments, self.chat, self.upgrade, self.copy = uploads, attachments, chat, upgrade, copy
        self.supply, self.hosts, self.desk = supply, hosts, desk
        self.stopping = threading.Event()
        self.applying = threading.Lock()
        self.clock_offset = 0.0
        self.sender = threading.Thread()

    def start(self) -> None:
        if not self.account.is_joined():
            return
        self.stopping.clear()
        self.sender = threading.Thread(target=self.repeated, args=(self.send,), daemon=True)
        self.sender.start()
        threading.Thread(target=self.repeated, args=(self.receive,), daemon=True).start()

    def stop(self) -> None:
        self.stopping.set()
        self.signal.ring()
        if self.sender.is_alive():
            self.sender.join(LAST_RETRY_SECONDS)

    def repeated(self, loop: Callable[[], None]) -> None:
        delay = FIRST_RETRY_SECONDS
        while not self.stopping.is_set():
            try:
                loop()
                delay = FIRST_RETRY_SECONDS
            except (OSError, TeamRefusal) as fault:
                self.status.failed(str(fault))
                self.stopping.wait(delay)
                delay = min(delay * 2, LAST_RETRY_SECONDS)

    def send(self) -> None:
        if self.account.is_upgrader():
            self.upgrade_finished()
        self.chat.renew()
        self.refill()
        batch = self.outgoing.sending_batch(BATCH_ROWS)
        self.upload_files()
        if not batch:
            self.signal.wait(IDLE_SECONDS)
            return
        answer = self.link.send_changes([change.payload() for change in batch], self.clock_offset, self.account.sequence(), self.hosts.keys())
        self.outgoing.sent(batch)
        self.rejected.apply(answer.settlement.rejected)
        self.handle_answer(answer.delivery)

    def upload_files(self) -> None:
        for upload in self.uploads.waiting():
            path = self.attachments.path(upload.row_table, upload.row, upload.name)
            if path.is_file():
                self.link.upload_file(FilePlace(upload.row_table, upload.row, upload.name), path.read_bytes())
            self.uploads.delete(upload, Actor.system())

    def upgrade_finished(self) -> None:
        while self.pulled(0):
            pass
        self.upgrade.finish()

    def refill(self) -> None:
        self.supply.refill()

    def receive(self) -> None:
        self.pulled(LONG_POLL_SECONDS)

    def pulled(self, wait_seconds: float) -> int:
        return self.handle_answer(self.link.fetch_changes(self.account.sequence(), wait_seconds, self.hosts.keys()))

    def handle_answer(self, answer: PullAnswer) -> int:
        count = self.applied(answer)
        self.desk.handle(answer.requests)
        self.status.connected()
        return count

    def applied(self, answer: PullAnswer) -> int:
        with self.applying:
            self.clock_offset = answer.server_time - time.time()
            if answer.copy_needed:
                self.download_copy()
                return 0
            sequence = self.account.sequence()
            changes = [TeamChange.logged(change) for change in answer.changes if change.sequence > sequence]
            self.incoming.apply(changes)
            self.account.record_pull(max(answer.head, sequence), answer.team_version)
            return len(changes)

    def download_copy(self) -> None:
        copy = self.link.full_copy()
        self.copy.replace(copy.rows, self.outgoing.rows())
        self.account.record_sequence(copy.head)

    def prepare_upgrade(self) -> None:
        self.upgrade.claim()
        while self.outgoing.waiting():
            self.send()
        while self.pulled(0):
            pass
