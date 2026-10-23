import sys
import threading
import time
import traceback

from journal.repositories.setting_rows import SettingRows

STALL_SECONDS = 5.0
CHECK_SECONDS = 1.0


class StallWatch:
    """While the Developer setting asks for it, the requests under way, by the thread that serves each: one still running after five seconds has every thread's stack written to the log, once a stall, so a stall names what holds it."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings
        self.running: dict[int, tuple[float, str]] = {}
        self.written: set[int] = set()
        self.lock = threading.Lock()
        self.watcher = threading.Thread(target=self.watch, name="stall-watch", daemon=True)

    def begin(self, path: str) -> None:
        from journal.features.faults.feature import Faults
        if not self.settings.option(Faults.STALL_STACKS):
            return
        with self.lock:
            self.running[threading.get_ident()] = (time.monotonic(), path)
            if not self.watcher.is_alive():
                self.watcher = threading.Thread(target=self.watch, name="stall-watch", daemon=True)
                self.watcher.start()

    def end(self) -> None:
        with self.lock:
            self.running.pop(threading.get_ident(), None)
            self.written.discard(threading.get_ident())

    def watch(self) -> None:
        while True:
            time.sleep(CHECK_SECONDS)
            with self.lock:
                overdue_requests = [(ident, path) for ident, (began, path) in self.running.items() if time.monotonic() - began > STALL_SECONDS and ident not in self.written]
                self.written.update(ident for ident, _ in overdue_requests)
            for ident, path in overdue_requests:
                self.write(ident, path)

    @staticmethod
    def write(overdue_thread: int, path: str) -> None:
        names = {thread.ident: thread.name for thread in threading.enumerate()}
        stacks = "".join(f"\n-- thread {names.get(ident, ident)}{' (the overdue request)' if ident == overdue_thread else ''}:\n{''.join(traceback.format_stack(frame))}" for ident, frame in sys._current_frames().items())
        sys.stderr.write(f"request {path} still running after {STALL_SECONDS:.0f} seconds; every thread's stack:{stacks}\n")
