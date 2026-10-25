import threading

from sync_service.carrier import Carrier, WATCH_SECONDS
from sync_service.journal_busy import JournalBusy
from sync_service.journal_doors import JournalDoors
from sync_service.journal_mismatch import JournalMismatch


class TeamCarriers:
    """A carrier for each team the journal joined beside its home team, each with loops of its own that carry that team's changes to its server and its server's back: started when the journal lists the team, stopped when it lists it no more."""

    def __init__(self, doors: JournalDoors) -> None:
        self.doors = doors
        self.carriers: dict[str, Carrier] = {}
        self.stopping = threading.Event()

    def started(self) -> "TeamCarriers":
        threading.Thread(target=self.run, name="team carriers", daemon=True).start()
        return self

    def run(self) -> None:
        self.watch()
        while not self.stopping.wait(WATCH_SECONDS):
            self.watch()

    def watch(self) -> None:
        try:
            keys = self.doors.teams()
        except (JournalBusy, JournalMismatch, OSError):
            return
        for key in keys:
            if key not in self.carriers:
                self.carriers[key] = Carrier(self.doors.bound(key)).started()
        for key in [key for key in self.carriers if key not in keys]:
            self.carriers.pop(key).stop()

    def stop(self) -> None:
        self.stopping.set()
        for carrier in self.carriers.values():
            carrier.stop()
