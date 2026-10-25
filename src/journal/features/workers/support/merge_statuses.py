from collections.abc import Callable, Iterator
from contextlib import contextmanager


class MergeStatuses:
    """What each source says it is doing while a worker's merge waits on the plugins, told as it comes to whoever runs that merge: the plugin by its name, the journal's own waiting with no name."""

    def __init__(self) -> None:
        self.writers: dict[int, list[Callable[[str], None]]] = {}

    @contextmanager
    def watched(self, worker: int, writer: Callable[[str], None]) -> Iterator[None]:
        self.writers.setdefault(worker, []).append(writer)
        try:
            yield
        finally:
            self.writers[worker].remove(writer)

    def report(self, worker: int, source: str, status: str) -> None:
        for writer in self.writers.get(worker, []):
            writer(f"{source}: {status}" if source else status)
