import sys
import threading
import time
import traceback

from journal.sync.commit_signal import CommitSignal
from journal.sync.sync_desk import SyncDesk
from journal.sync.sync_loop import SyncLoop
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink
from sync_server.pull_answer import PullAnswer

BATCH_ROWS = 200
IDLE_SECONDS = 5
LONG_POLL_SECONDS = 25
FIRST_RETRY_SECONDS = 1
LAST_RETRY_SECONDS = 30
OFFSET_TOLERANCE_SECONDS = 1.0
# how often the watchdog looks at the loops, and the longest each may rightly stay silent (a long poll and its request; a
# batch with its files and a copy)
WATCH_SECONDS = 5
RECEIVE_SILENCE_SECONDS = LONG_POLL_SECONDS + 35
SEND_SILENCE_SECONDS = 180


class SyncClient:
    """Carries a joined journal's sync to and from its team server, while the server's SyncDesk writes all it brings: a send loop takes the desk's next batch, sends the files waiting first so no change names a file the server lacks, pushes the batch and hands the desk the answer, woken by every commit that queues a change; a receive loop long-polls with the desk's query and hands it each answer; when an answer asks for the team's full copy the client downloads it and the desk lays it in. On a fault both wait 1, 2, 4 seconds and so on up to 30 and try again, and a watchdog starts a loop that ended again, logging why, and says sync stopped while a loop stays silent past its longest wait, so sync never stops without a word. The clock offset is measured from the server's time in each answer and sent with each push; it moves only when the measure differs by more than a second, since one that jitters by the answer's latency would let two writes a few milliseconds apart swap order on the server. Before an upgrade it takes the team's upgrade lease, sends the whole queue and pulls to the server's head; a journal that booted as the upgrader finishes the upgrade before its first batch."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, desk: SyncDesk, signal: CommitSignal, status: SyncStatus) -> None:
        self.account, self.link, self.desk, self.signal, self.status = account, link, desk, signal, status
        self.stopping = threading.Event()
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

    def retried(self, fault: str, delay: float) -> None:
        self.status.failed(fault)
        self.stopping.wait(delay)

    def send(self) -> None:
        if self.desk.is_upgrader():
            self.upgrade_finished()
        self.desk.kept_up()
        if not self.sent_batch():
            self.signal.wait(IDLE_SECONDS)

    def sent_batch(self) -> bool:
        with self.desk.held(self.desk.sending, "send a batch"):
            batch = self.desk.batch(BATCH_ROWS)
            self.upload_files()
            if not batch:
                return False
            answer = self.link.send_changes([change.payload() for change in batch], self.clock_offset, self.desk.query(0))
            self.measured(answer.delivery.server_time - time.time())
            self.copied_when_asked(answer.delivery)
            self.desk.pushed(batch, answer)
            return True

    def refill(self) -> None:
        self.desk.refill()

    def upload_files(self) -> None:
        for upload in self.desk.waiting_files():
            place, path = self.desk.file_place(upload)
            if path.is_file():
                self.link.upload_file(place, path.read_bytes())
            self.desk.file_sent(upload)

    def upgrade_finished(self) -> None:
        while self.pulled(0):
            pass
        self.desk.upgrade_finished()

    def receive(self) -> None:
        self.pulled(LONG_POLL_SECONDS)

    def pulled(self, wait_seconds: float) -> int:
        answer = self.link.fetch_changes(self.desk.query(wait_seconds))
        self.measured(answer.server_time - time.time())
        self.copied_when_asked(answer)
        return self.desk.answered(answer)

    def copied_when_asked(self, answer: PullAnswer) -> None:
        if not self.desk.needs_copy(answer):
            return
        with self.desk.laying_in():
            self.desk.copied(self.link.full_copy())

    def measured(self, offset: float) -> None:
        if abs(offset - self.clock_offset) > OFFSET_TOLERANCE_SECONDS:
            self.clock_offset = offset

    def prepare_upgrade(self) -> None:
        self.desk.upgrade_claimed()
        while self.desk.has_waiting():
            self.send()
        while self.pulled(0):
            pass
