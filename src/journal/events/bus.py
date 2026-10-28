import sys
import traceback

from journal.events.blocking import Blocking
from journal.events.event import Event
from journal.events.listener import Listener


class Bus:
    """Delivers each event to its listeners, the answer listeners first, those that run before the hook answers, each kept with the reason it runs then, and the background listeners after them, each in the order it was registered; dispatch_guarded logs a listener that raises and goes on, so the others still run, as a tick of the clock does."""

    def __init__(self) -> None:
        self._registered: list[tuple[type[Event], Listener, Blocking | None]] = []
        self._matched: dict[type[Event], list[tuple[Listener, Blocking | None]]] = {}

    def add_answer_listener(self, type_name: type[Event], listener: Listener, reason: Blocking) -> None:
        self._registered.append((type_name, listener, reason))
        self._matched.clear()

    def listen(self, type_name: type[Event], listener: Listener) -> None:
        self._registered.append((type_name, listener, None))
        self._matched.clear()

    def answer_listeners(self, type_name: type[Event]) -> list[Listener]:
        return [listener for listener, reason in self.matched(type_name) if reason or getattr(listener, "blocking", None)]

    def background_listeners(self, type_name: type[Event]) -> list[Listener]:
        return [listener for listener, reason in self.matched(type_name) if not (reason or getattr(listener, "blocking", None))]

    def listeners(self, type_name: type[Event]) -> list[Listener]:
        return [*self.answer_listeners(type_name), *self.background_listeners(type_name)]

    def matched(self, type_name: type[Event]) -> list[tuple[Listener, Blocking | None]]:
        if type_name not in self._matched:
            bases = set(type_name.__mro__)
            self._matched[type_name] = [(listener, reason) for registered, listener, reason in self._registered if registered in bases]
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
