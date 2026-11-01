from collections import deque
from math import ceil
from threading import Lock


class LoginThrottle:
    """Bounds failed hosted logins by source and across the whole hosted service."""

    def __init__(
        self,
        source_window: float = 300,
        source_limit: int = 5,
        source_lockout: float = 900,
        global_window: float = 60,
        global_limit: int = 64,
        global_lockout: float = 60,
        source_capacity: int = 1024,
    ) -> None:
        self.source_window, self.source_limit, self.source_lockout = source_window, source_limit, source_lockout
        self.global_window, self.global_limit, self.global_lockout = global_window, global_limit, global_lockout
        self.source_capacity = source_capacity
        self._sources: dict[str, tuple[deque[float], float]] = {}
        self._global_failures: deque[float] = deque()
        self._global_blocked_until = 0.0
        self._lock = Lock()

    def retry_after(self, source: str, now: float) -> int:
        with self._lock:
            self._prune(now)
            return max(
                self._seconds_left(self._global_blocked_until, now),
                self._seconds_left(self._blocked_until(source), now),
            )

    def failed(self, source: str, now: float) -> int:
        with self._lock:
            self._prune(now)
            if delay := self._seconds_left(self._global_blocked_until, now):
                return delay
            if delay := self._seconds_left(self._blocked_until(source), now):
                return delay
            failures, _ = self._sources.get(source, (deque(), 0.0))
            failures.append(now)
            self._global_failures.append(now)
            delay = self._delay(len(failures))
            if len(failures) >= self.source_limit:
                delay = ceil(self.source_lockout)
            if source not in self._sources and len(self._sources) >= self.source_capacity:
                del self._sources[next(iter(self._sources))]
            self._sources[source] = (failures, now + delay)
            if len(self._global_failures) >= self.global_limit:
                self._global_blocked_until = now + self.global_lockout
                delay = max(delay, ceil(self.global_lockout))
            return delay

    def succeeded(self, source: str) -> None:
        with self._lock:
            self._sources.pop(source, None)

    def _prune(self, now: float) -> None:
        while self._global_failures and self._global_failures[0] <= now - self.global_window:
            self._global_failures.popleft()
        for source, (failures, blocked_until) in tuple(self._sources.items()):
            while failures and failures[0] <= now - self.source_window:
                failures.popleft()
            if not failures and blocked_until <= now:
                del self._sources[source]
        if self._global_blocked_until <= now:
            self._global_blocked_until = 0.0

    def _blocked_until(self, source: str) -> float:
        return self._sources.get(source, (deque(), 0.0))[1]

    @staticmethod
    def _delay(failures: int) -> int:
        return min(30, 2 ** (failures - 1))

    @staticmethod
    def _seconds_left(until: float, now: float) -> int:
        return max(0, ceil(until - now))
