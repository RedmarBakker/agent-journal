import contextvars
import queue
import sys
import threading
from typing import Callable

from journal.support.fault_log import FaultLog


class ListenerQueue:
    """Work the server does after it has replied: one worker thread, in order, never on a request's thread, each piece in the scope it was added in."""

    STOP = None
    QUEUE_WARNING_ITEMS = 500
    LOG_SKIPS = 100

    def __init__(self, faults: FaultLog) -> None:
        self.faults = faults
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self.skipped = 0

    def start(self) -> None:
        self._thread = threading.Thread(target=self._work, name="deferred", daemon=True)
        self._thread.start()

    def add(self, work: Callable[[], object]) -> None:
        self._queue.put(lambda context=contextvars.copy_context(): context.run(work))

    def add_bounded(self, work: Callable[[], object], subject: str) -> None:
        if self.depth() < self.QUEUE_WARNING_ITEMS:
            self.add(work)
            return
        if self.skipped % self.LOG_SKIPS == 0:
            sys.stderr.write(f"deferred work is {self.depth()} pieces behind: skipped {subject} ({self.skipped + 1} skipped so far)\n")
        self.skipped += 1

    def depth(self) -> int:
        return self._queue.qsize()

    def stop(self) -> None:
        if self._thread:
            self._queue.put(self.STOP)
            self._thread.join()
            self._thread = None

    def drain(self) -> None:
        if self._thread is None:
            self.run_waiting()
            return
        self._queue.join()

    def run_waiting(self) -> None:
        while not self._queue.empty():
            self.run_one(self._queue.get())

    def _work(self) -> None:
        while (work := self._queue.get()) is not self.STOP:
            self.run_one(work)
        self._queue.task_done()

    def run_one(self, work: Callable[[], object]) -> None:
        try:
            work()
        except Exception as fault:
            self.faults.reported("deferred work", fault)
        finally:
            self._queue.task_done()
