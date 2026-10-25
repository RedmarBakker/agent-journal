from collections.abc import Callable, Iterator
from contextlib import contextmanager


class MergeStatuses:
    """What each source says it is doing while a worker's merge waits on the plugins, told as it comes to whoever runs that merge: the plugin by its name, the journal's own waiting with no name."""

    def __init__(self) -> None:
        self.writers: dict[int, Callable[[str], None]] = {}

    @contextmanager
    def watched(self, worker: int, writer: Callable[[str], None]) -> Iterator[None]:
        self.writers[worker] = writer
        try:
            yield
        finally:
            del self.writers[worker]

    def report(self, worker: int, source: str, status: str) -> None:
        writer = self.writers.get(worker)
        if writer:
            writer(f"{source}: {status}" if source else status)
