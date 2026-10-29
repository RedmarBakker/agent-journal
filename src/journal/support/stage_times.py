import threading
import time
from contextlib import contextmanager


class StageTimes:
    """The time each stage of the journal's work took, stored in memory until the Developer numbers take them: reading a feature's facts, each listener of a hook, recording its entry, and a hook's time before the server read it and before it was handled."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.samples: list[tuple[str, int]] = []

    @contextmanager
    def timed(self, stage: str):
        began = time.perf_counter()
        try:
            yield
        finally:
            self.add(stage, time.perf_counter() - began)

    def add(self, stage: str, seconds: float) -> None:
        with self.lock:
            self.samples.append((stage, round(seconds * 1000)))

    def drained(self) -> list[tuple[str, int]]:
        with self.lock:
            samples, self.samples = self.samples, []
        return samples
