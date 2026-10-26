import threading
import time as timing
from journal.support.time_source import TimeSource


class RecentCounts:
    """How often something was sent from a key in the last period of time, so a visitor cannot repeat it without limit; a subclass sets how many and how long."""

    MAXIMUM_COUNT = 0
    WINDOW_SECONDS = 0

    def __init__(self, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.lock = threading.Lock()
        self.tries: dict[str, list[float]] = {}

    def recent(self, key: str) -> list[float]:
        start = self.time_source.seconds() - self.WINDOW_SECONDS
        return [time for time in self.tries.get(key, []) if time > start]

    def locked(self, key: str) -> bool:
        with self.lock:
            return len(self.recent(key)) >= self.MAXIMUM_COUNT

    def count(self, key: str) -> None:
        with self.lock:
            self.tries[key] = [*self.recent(key), self.time_source.seconds()]
