import threading

from journal.events.bus import Bus
from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged


class WorkerMergeWait(Listener[WorkerWorkMerged]):
    """Waits for one worker's work-merged event."""

    def __init__(self, bus: Bus, worker: int) -> None:
        self.worker = worker
        self.finished = threading.Event()
        bus.listen(WorkerWorkMerged, self)

    def handle(self, event: WorkerWorkMerged) -> None:
        if event.worker == self.worker:
            self.finished.set()

    def wait(self) -> None:
        if not self.finished.wait(5):
            raise AssertionError(f"worker {self.worker} did not finish merging")
