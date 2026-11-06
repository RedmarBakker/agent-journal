import threading

from journal.events.bus import Bus
from journal.events.listener import Listener
from journal.events.rows.check_completed import CheckCompleted


class CheckRunWait(Listener[CheckCompleted]):
    """Waits for one scheduled check run to finish."""

    def __init__(self, bus: Bus, check: int) -> None:
        self.check = check
        self.finished = threading.Event()
        bus.listen(CheckCompleted, self)

    def handle(self, event: CheckCompleted) -> None:
        if event.check_id == self.check:
            self.finished.set()

    def wait(self) -> None:
        if not self.finished.wait(5):
            raise TimeoutError(f"check {self.check} did not finish its scheduled run")
