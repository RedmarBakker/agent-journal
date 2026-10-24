import sys
import traceback

from journal.events.event import Event
from journal.events.listener import Listener


class Bus:
    def __init__(self) -> None:
        self._listeners: list[tuple[type[Event], Listener]] = []
        self._matched: dict[type[Event], list[Listener]] = {}

    def listen(self, kind: type[Event], listener: Listener) -> None:
        self._listeners.append((kind, listener))
        self._matched.clear()

    def listeners(self, kind: type[Event]) -> list[Listener]:
        if kind not in self._matched:
            bases = set(kind.__mro__)
            self._matched[kind] = [listener for registered, listener in self._listeners if registered in bases]
        return self._matched[kind]

    def dispatch(self, event: Event) -> list[object]:
        return [listener.handle(event) for listener in self.listeners(type(event))]

    # every listener hears the event, one that raises logged and passed over, so the others still run, as a tick of the clock does
    def dispatch_guarded(self, event: Event) -> list[object]:
        answers = []
        for listener in self.listeners(type(event)):
            try:
                answers.append(listener.handle(event))
            except Exception:
                sys.stderr.write(f"{type(listener).__name__} failed on {type(event).__name__}:\n{traceback.format_exc()}")
        return answers
