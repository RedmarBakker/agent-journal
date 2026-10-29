import threading
from contextlib import contextmanager


class AnswerPhase:
    """The listener a hook runs before its answer on this thread, and the viewer writes made while it ran: the receiver opens it around each such listener, the viewer's writers report to it, and an announcement made inside it waits until after the answer."""

    def __init__(self) -> None:
        self.local = threading.local()

    @contextmanager
    def running(self, listener: str):
        self.local.listener, self.local.writers = listener, []
        try:
            yield
        finally:
            self.local.listener = ""

    def is_open(self) -> bool:
        return bool(getattr(self.local, "listener", ""))

    def record_viewer_write(self, writer: str) -> None:
        if self.is_open():
            self.local.writers.append(writer)

    def writers(self) -> list[str]:
        return list(getattr(self.local, "writers", []))
