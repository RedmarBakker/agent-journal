from journal.events.bus import Bus
from journal.events.event import Event


class Announcer:
    """Dispatches an event that no row's save and no hook carries, a moment worth a mark in the chat, to the listeners that hear it."""

    def __init__(self, bus: Bus) -> None:
        self.bus = bus

    def announce(self, event: Event) -> None:
        self.bus.dispatch(event)
