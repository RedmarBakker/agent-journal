from threading import Lock
from journal.support.timeout import Timeout
from journal.support.time_source import TimeSource

VIEWER_WINDOW_SECONDS = 15.0
VIEWER = "x-journal-viewer"


class ViewerPresence:
    """When a viewer tab last contacted the journal, stored in memory: a launch checks it before opening a new tab."""

    def __init__(self, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.time = 0.0
        self.lock = Lock()
        self.environment_switch = (0, "", 0.0)

    def record(self, headers: dict) -> None:
        if headers.get(VIEWER):
            self.time = self.time_source.seconds()

    def open(self) -> bool:
        return not Timeout.seconds(VIEWER_WINDOW_SECONDS).started(self.time).is_elapsed(self.time_source.seconds())

    def switch_to(self, environment: str) -> int:
        with self.lock:
            sequence = self.environment_switch[0] + 1
            self.environment_switch = (sequence, environment, self.time_source.seconds())
            return sequence

    def switch_after(self, sequence: int) -> tuple[int, str] | None:
        with self.lock:
            signal = self.environment_switch
        if signal[0] <= sequence or Timeout.seconds(VIEWER_WINDOW_SECONDS).started(signal[2]).is_elapsed(self.time_source.seconds()):
            return None
        return signal[0], signal[1]
