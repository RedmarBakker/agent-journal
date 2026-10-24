import sys
import threading
import time
import traceback
from pathlib import Path

from sync_service.journal_busy import JournalBusy
from sync_service.journal_doors import JournalDoors
from sync_service.journal_mismatch import JournalMismatch
from sync_service.loop import Loop
from sync_service.team_link import TeamLink
from sync_service.team_refusal import TeamRefusal

NAME = "sync"
EVENTS = ("change_queued", "team_joined", "team_left", "upgrade_preparing", "upgrade_abandoned")
IDLE_SECONDS = 5
LONG_POLL_SECONDS = 25
FIRST_RETRY_SECONDS = 1
LAST_RETRY_SECONDS = 30
BEAT_SECONDS = 1
# how often the watchdog looks at the loops, and the longest each may rightly stay silent (a long poll and its request; a
# batch with its files and a copy)
WATCH_SECONDS = 5
RECEIVE_SILENCE_SECONDS = LONG_POLL_SECONDS + 35
SEND_SILENCE_SECONDS = 180


class Carrier:
    """Carries a journal's changes to its team server and the team's back, the journal server writing all it brings: a send loop takes the server's next batch when a change is queued or every few seconds, sends its files first so no change names a file the team lacks, pushes it and hands the server the answer; a receive loop long-polls the team with the server's query and hands it each answer; when the server needs the team's full copy for an answer the carrier downloads it, the server lays it in, and the answer is handed again, nothing of this journal's going out meanwhile. On a fault both wait 1, 2, 4 seconds and so on up to 30 and try again, quietly while the journal server is down or starting, and a watchdog starts a loop that ended again and reports one silent past its longest wait. Every second it reports how it stands to the server and registers with it again when the server's secret is new. It waits quietly while the journal is in no team, and an upgrade's drain leaves it paused until the server starts again or the upgrade is abandoned."""

    def __init__(self, doors: JournalDoors) -> None:
        self.doors = doors
        self.fault, self.reached, self.busy = "", False, ""
        self.address, self.registered_secret, self.paused_secret = "", "", ""
        self.carrying = threading.Lock()
        self.stopping = threading.Event()
        self.sending_loop = Loop("send", self.send, SEND_SILENCE_SECONDS)
        self.receiving_loop = Loop("receive", self.receive, RECEIVE_SILENCE_SECONDS)
        self.loops = (self.sending_loop, self.receiving_loop)
        self.handlers = {"change_queued": self.change_queued, "team_joined": self.team_joined, "team_left": self.ignored, "upgrade_preparing": self.drained, "upgrade_abandoned": self.abandoned}

    def run(self, address: str) -> None:
        self.address = address
        for loop in self.loops:
            loop.started(self.repeated)
        watched_at = time.monotonic()
        while not self.stopping.wait(BEAT_SECONDS):
            self.beat()
            if time.monotonic() - watched_at >= WATCH_SECONDS:
                self.watch()
                watched_at = time.monotonic()

    def stop(self) -> None:
        self.stopping.set()
        for loop in self.loops:
            loop.wake.set()

    def heard(self, event: dict) -> dict:
        return self.handlers.get(event.get("event", ""), self.ignored)()

    def change_queued(self) -> dict:
        self.sending_loop.wake.set()
        return {}

    def team_joined(self) -> dict:
        for loop in self.loops:
            loop.wake.set()
        return {}

    def ignored(self) -> dict:
        return {}

    # the whole queue sent and the team pulled to its head under the team's upgrade lease, then nothing more until the server starts again
    def drained(self) -> dict:
        self.paused_secret = self.doors.secret()
        team = TeamLink(self.doors.team())
        self.doors.upgrade_claimed()
        while self.carried(team, self.doors.batch()):
            pass
        while self.pulled(team, 0):
            pass
        return {"drained": True}

    def abandoned(self) -> dict:
        self.paused_secret = ""
        return self.team_joined()

    def is_paused(self) -> bool:
        return bool(self.paused_secret) and self.paused_secret == self.doors.secret()

    def beat(self) -> None:
        try:
            secret = self.doors.secret()
            if secret and secret != self.registered_secret:
                self.doors.register(NAME, self.address, EVENTS)
                self.registered_secret = secret
                self.team_joined()
            self.doors.state(self.fault, self.reached)
        except JournalBusy:
            return
        except (OSError, JournalMismatch) as fault:
            self.fault = str(fault)

    def watch(self) -> None:
        for loop in self.loops:
            if loop.is_dead() and not self.stopping.is_set():
                sys.stderr.write(f"the sync {loop.name} loop ended: started again\n")
                loop.started(self.repeated)
            elif loop.is_silent():
                self.fault = f"sync stopped: its {loop.name} loop has been silent for {loop.silence_seconds():.0f} seconds"

    def repeated(self, loop: Loop, generation: int) -> None:
        delay = FIRST_RETRY_SECONDS
        try:
            while not self.stopping.is_set() and loop.is_current(generation):
                loop.beat()
                try:
                    loop.step()
                    self.busy = ""
                    delay = FIRST_RETRY_SECONDS
                except JournalBusy as busy:
                    if str(busy) != self.busy:
                        sys.stderr.write(f"sync waits: {busy}\n")
                    self.busy = str(busy)
                    loop.rest(delay)
                    delay = min(delay * 2, LAST_RETRY_SECONDS)
                except (OSError, TeamRefusal, JournalMismatch) as fault:
                    self.retried(loop, str(fault), delay)
                    delay = min(delay * 2, LAST_RETRY_SECONDS)
                except Exception as fault:
                    sys.stderr.write(f"the sync {loop.name} loop failed and tries again:\n{traceback.format_exc()}")
                    self.retried(loop, f"{type(fault).__name__}: {fault}", delay)
                    delay = min(delay * 2, LAST_RETRY_SECONDS)
        except BaseException:
            sys.stderr.write(f"the sync {loop.name} loop ended:\n{traceback.format_exc()}")
            raise

    def retried(self, loop: Loop, fault: str, delay: float) -> None:
        if fault != self.fault:
            sys.stderr.write(f"sync: {fault}; trying again\n")
        self.fault = fault
        loop.rest(delay)

    def connected(self) -> None:
        self.fault = ""
        self.reached = True

    # the team as the journal server says to reach it, or none while the journal is in no team or an upgrade holds the sync
    def team(self) -> TeamLink | None:
        team = self.doors.team()
        if not team["joined"] or self.is_paused():
            return None
        return TeamLink(team)

    def send(self) -> None:
        team = self.team()
        if team is None:
            self.sending_loop.rest(IDLE_SECONDS)
            return
        batch = self.doors.batch()
        if batch["upgrader"]:
            self.upgrade_finished(team)
        if not self.carried(team, batch):
            self.sending_loop.rest(IDLE_SECONDS)

    # the batch's files sent first, then its changes pushed and the answer handed to the server; whether it held changes to push
    def carried(self, team: TeamLink, batch: dict) -> bool:
        with self.carrying:
            for file in batch["files"]:
                if Path(file["path"]).is_file():
                    team.upload(file["address"], Path(file["path"]).read_bytes())
            if batch["files"]:
                self.doors.files_sent([file["id"] for file in batch["files"]])
            if not batch["ids"]:
                return False
            answer = team.push(batch["push"])
            self.connected()
            if self.doors.pushed(batch["ids"], answer)["needs_copy"]:
                self.laid_in(team)
                self.doors.answered(answer["delivery"])
            return True

    def upgrade_finished(self, team: TeamLink) -> None:
        while self.pulled(team, 0):
            pass
        self.doors.upgrade_finished()

    def receive(self) -> None:
        team = self.team()
        if team is None:
            self.receiving_loop.rest(IDLE_SECONDS)
            return
        self.pulled(team, LONG_POLL_SECONDS)

    def pulled(self, team: TeamLink, wait_seconds: float) -> int:
        query = self.doors.query(wait_seconds)
        answer = team.pull(query["path"], wait_seconds)
        self.connected()
        return self.taken(team, answer)

    # an answer handed to the server, the team's full copy laid in first when it needs it, while nothing of this journal's goes out
    def taken(self, team: TeamLink, answer: dict) -> int:
        taken = self.doors.answered(answer)
        if taken["needs_copy"]:
            with self.carrying:
                self.laid_in(team)
                taken = self.doors.answered(answer)
        return taken["applied"]

    def laid_in(self, team: TeamLink) -> None:
        self.doors.copied(team.full_copy())
