import sys
import traceback

from journal.events.event import Event
from journal.events.listener import Listener


class Bus:
    """Delivers each event to its listeners; dispatch_guarded logs a listener that raises and goes on, so the others still run, as a tick of the clock does."""

    def __init__(self) -> None:
        self._listeners: list[tuple[type[Event], Listener]] = []
        self._matched: dict[type[Event], list[Listener]] = {}

    def listen(self, type_name: type[Event], listener: Listener) -> None:
        self._listeners.append((type_name, listener))
        self._matched.clear()

    def listeners(self, type_name: type[Event]) -> list[Listener]:
        if type_name not in self._matched:
            bases = set(type_name.__mro__)
            self._matched[type_name] = [listener for registered, listener in self._listeners if registered in bases]
        return self._matched[type_name]

    def dispatch(self, event: Event) -> list[object]:
        return [listener.handle(event) for listener in self.listeners(type(event))]

    def dispatch_guarded(self, event: Event) -> list[object]:
        answers = []
        for listener in self.listeners(type(event)):
            try:
                answers.append(listener.handle(event))
            except Exception:
                sys.stderr.write(f"{type(listener).__name__} failed on {type(event).__name__}:\n{traceback.format_exc()}")
        return answers
