from functools import partial

from journal.events.bus import Bus
from journal.events.event import Event
from journal.support.answer_phase import AnswerPhase
from journal.support.listener_queue import ListenerQueue


class Announcer:
    """Dispatches an event that no row's save and no hook carries, a moment worth a mark in the chat, to the listeners that hear it; one announced while a hook waits for its answer is dispatched after the answer, by the deferred worker."""

    def __init__(self, bus: Bus, phase: AnswerPhase, deferred: ListenerQueue) -> None:
        self.bus, self.phase, self.deferred = bus, phase, deferred

    def announce(self, event: Event) -> list[object]:
        if self.phase.is_open():
            self.deferred.add(partial(self.bus.dispatch, event))
            return []
        return self.bus.dispatch(event)
