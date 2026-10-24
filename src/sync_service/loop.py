import threading
import time
from typing import Callable


class Loop:
    """One of the sync service's loops as the watchdog sees it: the step it repeats, the longest a step may rightly stay silent, the thread that runs it, its generation, which a loop started again moves so an older thread that wakes ends instead of running beside it, when it last showed it was alive, and what wakes it from a rest."""

    def __init__(self, name: str, step: Callable[[], None], longest_silence_seconds: float) -> None:
        self.name, self.step, self.longest_silence_seconds = name, step, longest_silence_seconds
        self.generation = 0
        self.beat_at = time.monotonic()
        self.thread = threading.Thread()
        self.wake = threading.Event()

    def started(self, runner: Callable[["Loop", int], None]) -> None:
        self.generation += 1
        self.beat()
        self.thread = threading.Thread(target=runner, args=(self, self.generation), name=f"sync {self.name}", daemon=True)
        self.thread.start()

    # waits the seconds given, or until something wakes the loop sooner
    def rest(self, seconds: float) -> None:
        self.wake.wait(seconds)
        self.wake.clear()

    def beat(self) -> None:
        self.beat_at = time.monotonic()

    def is_current(self, generation: int) -> bool:
        return generation == self.generation

    def is_dead(self) -> bool:
        return not self.thread.is_alive()

    def silence_seconds(self) -> float:
        return time.monotonic() - self.beat_at

    def is_silent(self) -> bool:
        return self.silence_seconds() > self.longest_silence_seconds
