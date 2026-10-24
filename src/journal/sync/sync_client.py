import sys
import threading
import time
import traceback

from pathlib import Path

from journal.sync.desk_busy import DeskBusy
from journal.sync.desk_doors import DeskDoors
from journal.sync.sync_batch import SyncBatch
from journal.sync.sync_loop import SyncLoop
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink
from sync_server.pull_answer import PullAnswer

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
    """Carries a joined journal's sync to and from its team server, while the server's SyncDesk writes all it brings, reached through its doors in the server's own process or from a process of its own (DeskDoors): a send loop takes the desk's next batch, waiting for a commit that queues a change, sends the files waiting first so no change names a file the server lacks, pushes the batch and hands the desk the answer; a receive loop long-polls with the desk's query and hands it each answer; when the desk needs the team's full copy for an answer the client downloads it, the desk lays it in, and the answer is handed again, nothing of this journal's going out meanwhile. On a fault both wait 1, 2, 4 seconds and so on up to 30 and try again, and a watchdog starts a loop that ended again, logging why, and says sync stopped while a loop stays silent past its longest wait, so sync never stops without a word. The clock offset is measured from the server's time in each answer and sent with each push; it moves only when the measure differs by more than a second, since one that jitters by the answer's latency would let two writes a few milliseconds apart swap order on the server. Before an upgrade it takes the team's upgrade lease, sends the whole queue and pulls to the server's head; a journal that booted as the upgrader finishes the upgrade before its first batch."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, doors: DeskDoors, status: SyncStatus) -> None:
        self.account, self.link, self.doors, self.status = account, link, doors, status
        self.carrying = threading.Lock()
        self.busy = ""
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
        self.doors.wake()
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
                    self.busy = ""
                    delay = FIRST_RETRY_SECONDS
                except DeskBusy as busy:
                    if str(busy) != self.busy:
                        sys.stderr.write(f"sync waits: {busy}\n")
                    self.busy = str(busy)
                    self.stopping.wait(delay)
                    delay = min(delay * 2, LAST_RETRY_SECONDS)
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
        if fault != self.status.fault:
            sys.stderr.write(f"sync: {fault}; trying again\n")
        self.status.failed(fault)
        self.stopping.wait(delay)

    def send(self) -> None:
        batch = self.doors.batch(IDLE_SECONDS)
        if batch.upgrader:
            self.upgrade_finished()
        self.carried(batch)

    # the batch's files sent first, then its changes pushed and the answer handed to the desk; whether it held changes to push
    def carried(self, batch: SyncBatch) -> bool:
        with self.carrying:
            for file in batch.files:
                if Path(file.path).is_file():
                    self.link.upload_file(file.place, Path(file.path).read_bytes())
            if batch.files:
                self.doors.files_sent(tuple(file.id for file in batch.files))
            if not batch.ids:
                return False
            answer = self.link.send_changes(list(batch.changes), self.clock_offset, self.doors.query(0))
            self.status.connected()
            self.measured(answer.delivery.server_time - time.time())
            if self.doors.pushed(batch, answer).needs_copy:
                self.laid_in()
                self.doors.answered(answer.delivery)
            return True

    def upgrade_finished(self) -> None:
        while self.pulled(0):
            pass
        self.doors.upgrade_finished()

    def receive(self) -> None:
        self.pulled(LONG_POLL_SECONDS)

    def pulled(self, wait_seconds: float) -> int:
        answer = self.link.fetch_changes(self.doors.query(wait_seconds))
        self.status.connected()
        self.measured(answer.server_time - time.time())
        return self.taken(answer)

    # an answer handed to the desk, the team's full copy laid in first when the desk needs it, while nothing of this journal's goes out
    def taken(self, answer: PullAnswer) -> int:
        taken = self.doors.answered(answer)
        if taken.needs_copy:
            with self.carrying:
                self.laid_in()
                taken = self.doors.answered(answer)
        return taken.applied

    def laid_in(self) -> None:
        self.doors.copied(self.link.full_copy())

    def measured(self, offset: float) -> None:
        if abs(offset - self.clock_offset) > OFFSET_TOLERANCE_SECONDS:
            self.clock_offset = offset

    def prepare_upgrade(self) -> None:
        self.doors.upgrade_claimed()
        while self.carried(self.doors.batch(0)):
            pass
        while self.pulled(0):
            pass
