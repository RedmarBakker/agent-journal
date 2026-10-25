import threading
from collections.abc import Iterator
from contextlib import contextmanager


class Merger:
    """The one funnel for git work on the project's branch: every merge, a worker's or a command that merges, waits for its turn here and runs alone, in the order the turns were asked for; whatever comes before it, such as the plugins' checks, runs side by side."""

    def __init__(self) -> None:
        self.condition = threading.Condition()
        self.tickets = 0
        self.serving = 0

    @contextmanager
    def turn(self) -> Iterator[int]:
        with self.condition:
            ticket = self.tickets
            self.tickets += 1
            waiting = ticket - self.serving
            self.condition.wait_for(lambda: self.serving == ticket)
        try:
            yield waiting
        finally:
            with self.condition:
                self.serving += 1
                self.condition.notify_all()

    def queued(self) -> int:
        with self.condition:
            return self.tickets - self.serving
