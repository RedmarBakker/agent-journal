import sys
import threading
import time
import traceback
from contextlib import contextmanager

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
from journal.sync.pull_queries import PullQueries
from sync_server.pull_answer import PullAnswer
from journal.sync.sync_loop import SyncLoop

BATCH_ROWS = 200
IDLE_SECONDS = 5
LONG_POLL_SECONDS = 25
FIRST_RETRY_SECONDS = 1
LAST_RETRY_SECONDS = 30
OFFSET_TOLERANCE_SECONDS = 1.0
# how often the watchdog looks at the loops, the longest each may rightly stay silent (a long poll and its request; a
# batch with its files and a copy), and the longest a loop waits for the other's lock before that is a fault
WATCH_SECONDS = 5
RECEIVE_SILENCE_SECONDS = LONG_POLL_SECONDS + 35
SEND_SILENCE_SECONDS = 180
LOCK_SECONDS = 120


class SyncClient:
    """Keeps a joined journal in step with its team: a send loop pushes the queued changes oldest first in batches, woken by every commit that queues one, and a receive loop long-polls for the team's changes and applies them. On a fault both wait 1, 2, 4 seconds and so on up to 30 and try again; a change is removed from the queue only once the server answered for it, and the edits it rejected are put right here; once it has taken a batch it sends every file attached here that the server lacks, before the batch, so no change in it names a file the server has not got, renews the Team chat's lease while this machine holds it, and asks for a block of row numbers for every shared table that holds less than a block and a fifth. Every push carries a pull, so its answer brings the team's changes as the long poll does, and both bring the writes waiting for the environments this journal hosts, which its host desk makes; changes are applied one answer at a time and only past the sequence this journal holds, so the two loops never apply one twice; one batch is sent at a time, so the upgrade's own sends and the send loop never race an older write past a newer one, which the server would reject as an edit lost to a later one. The clock offset is measured from the server's time in each pull answer and sent with each push; it moves only when the measure differs by more than a second, since a measure that jitters by the answer's latency would let two of this journal's writes a few milliseconds apart swap order on the server, which then rejects the newer as lost to the older. Before an upgrade it takes the team's upgrade lease, sends its whole queue and pulls to the server's head; a journal that booted as the upgrader finishes the upgrade before its loops start, and one behind another's upgrade takes the team's copy in place of its shared rows. A watchdog starts a loop that ended again, logging why it ended, says sync stopped on the status line while a loop stays silent past its longest wait, and a lock waited on past its limit is a fault, so sync never stops without a word."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, outgoing: OutgoingChanges, incoming: IncomingChanges, rejected: RejectedEdits, signal: CommitSignal, status: SyncStatus, uploads: PendingUploads, attachments: Attachments, chat: TeamChat, upgrade: TeamUpgrade, copy: JournalCopy, supply: BlockSupply, queries: PullQueries, desk: HostDesk) -> None:
        self.account, self.link, self.outgoing, self.incoming, self.rejected, self.signal, self.status = account, link, outgoing, incoming, rejected, signal, status
        self.uploads, self.attachments, self.chat, self.upgrade, self.copy = uploads, attachments, chat, upgrade, copy
        self.supply, self.queries, self.desk = supply, queries, desk
        self.stopping = threading.Event()
        self.applying, self.sending = threading.Lock(), threading.RLock()
        self.clock_offset = 0.0
        self.sending_loop = SyncLoop("send", self.send, SEND_SILENCE_SECONDS)
        self.loops = (self.sending_loop, SyncLoop("receive", self.receive, RECEIVE_SILENCE_SECONDS))

    def start(self) -> None:
        if not self.account.is_joined():
            return
        self.stopping.clear()
        for loop in self.loops:
            loop.started(self.repeated)
        threading.Thread(target=self.watched, name="sync watchdog", daemon=True).start()

    def stop(self) -> None:
        self.stopping.set()
        self.signal.ring()
        if not self.sending_loop.is_dead():
            self.sending_loop.thread.join(LAST_RETRY_SECONDS)

    def watched(self) -> None:
        while not self.stopping.wait(WATCH_SECONDS):
            self.watch()

    def watch(self) -> None:
        for loop in self.loops:
            if loop.is_dead():
                sys.stderr.write(f"the sync {loop.name} loop ended: started again\n")
                loop.started(self.repeated)
            elif loop.is_silent():
                self.status.failed(f"sync stopped: its {loop.name} loop has been silent for {loop.silence_seconds():.0f} seconds")

    def repeated(self, loop: SyncLoop, generation: int) -> None:
        delay = FIRST_RETRY_SECONDS
        try:
            while not self.stopping.is_set() and loop.is_current(generation):
                loop.beat()
                try:
                    loop.step()
                    delay = FIRST_RETRY_SECONDS
                except (OSError, TeamRefusal) as fault:
                    self.retried(str(fault), delay)
                    delay = min(delay * 2, LAST_RETRY_SECONDS)
                except Exception as fault:
                    sys.stderr.write(f"the sync {loop.name} loop failed and tries again:\n{traceback.format_exc()}")
                    self.retried(f"{type(fault).__name__}: {fault}", delay)
                    delay = min(delay * 2, LAST_RETRY_SECONDS)
        except BaseException:
            sys.stderr.write(f"the sync {loop.name} loop ended:\n{traceback.format_exc()}")
            raise

    @staticmethod
    @contextmanager
    def held(lock, purpose: str):
        if not lock.acquire(timeout=LOCK_SECONDS):
            raise TimeoutError(f"the sync waited {LOCK_SECONDS} seconds to {purpose}, held by its other loop all that time")
        try:
            yield
        finally:
            lock.release()

    def retried(self, fault: str, delay: float) -> None:
        self.status.failed(fault)
        self.stopping.wait(delay)

    def send(self) -> None:
        if self.account.is_upgrader():
            self.upgrade_finished()
        self.chat.renew()
        self.refill()
        if not self.sent_batch():
            self.signal.wait(IDLE_SECONDS)

    def sent_batch(self) -> bool:
        with self.held(self.sending, "send a batch"):
            batch = self.outgoing.sending_batch(BATCH_ROWS)
            self.upload_files()
            if not batch:
                return False
            self.delivered(batch)
            return True

    def delivered(self, batch: list) -> None:
        answer = self.link.send_changes([change.payload() for change in batch], self.clock_offset, self.queries.query(0))
        self.measured(answer.delivery.server_time - time.time())
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
        answer = self.link.fetch_changes(self.queries.query(wait_seconds))
        self.measured(answer.server_time - time.time())
        return self.handle_answer(answer)

    def handle_answer(self, answer: PullAnswer) -> int:
        count = self.applied(answer)
        self.desk.handle(answer.requests)
        self.status.connected()
        return count

    def applied(self, answer: PullAnswer) -> int:
        if answer.copy_needed and self.account.sequence() < answer.head:
            sys.stderr.write(f"the team asked for its full copy: this journal holds sequence {self.account.sequence()}, the team's head is {answer.head}\n")
            # nothing of this journal's goes out between the team's copy being taken and laid in place of its rows, or the copy would
            # wipe a change sent meanwhile, which no pull sends back, as a journal is never sent its own changes
            with self.held(self.sending, "lay in the team's copy"), self.held(self.applying, "lay in the team's copy"):
                self.download_copy()
            return 0
        with self.held(self.applying, "apply the team's changes"):
            sequence = self.account.sequence()
            changes = [TeamChange.logged(change) for change in answer.changes if change.sequence > sequence]
            self.incoming.apply(changes)
            self.account.record_pull(max(answer.head, sequence), answer.team_version)
            return len(changes)

    def measured(self, offset: float) -> None:
        if abs(offset - self.clock_offset) > OFFSET_TOLERANCE_SECONDS:
            self.clock_offset = offset

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
