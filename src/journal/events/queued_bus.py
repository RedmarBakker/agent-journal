from journal.events.bus import Bus
from journal.events.event import Event
from journal.events.models.model_event import ModelEvent
from journal.events.rows.row_event import RowEvent
from journal.support.listener_queue import ListenerQueue


class QueuedBus(Bus):
    """The bus the journal runs on: a row's event has its answer listeners run in the writer's thread to give their answers, and every other listener run after the answer, on the deferred queue, in the scope the event was dispatched in; any other event reaches every listener in place."""

    QUEUED_EVENTS = (ModelEvent, RowEvent)

    def __init__(self, queue: ListenerQueue) -> None:
        super().__init__()
        self.queue = queue

    def dispatch(self, event: Event) -> list[object]:
        if not isinstance(event, self.QUEUED_EVENTS):
            return super().dispatch(event)
        return self.queued_dispatch(event)

    def queued_dispatch(self, event: Event) -> list[object]:
        answers = [listener.handle(event) for listener in self.answer_listeners(type(event))]
        for listener in self.background_listeners(type(event)):
            self.queue.add(lambda listener=listener: listener.handle(event))
        return answers
