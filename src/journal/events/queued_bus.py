from contextvars import copy_context
from functools import partial

from journal.db.commit_queue import CommitQueue
from journal.events.bus import Bus
from journal.events.event import Event
from journal.events.models.model_event import ModelEvent
from journal.events.rows.row_event import RowEvent
from journal.support.listener_queue import ListenerQueue


class QueuedBus(Bus):
    """The bus the journal runs on: a row's event has its answer listeners run in the writer's thread to give their answers, and every other listener queued first once the write commits, so the events its answer listeners raise are heard after it, and run after the answer, on the deferred queue, in the scope the event was dispatched in; any other event reaches every listener in place."""

    QUEUED_EVENTS = (ModelEvent, RowEvent)

    def __init__(self, queue: ListenerQueue, commits: CommitQueue) -> None:
        super().__init__()
        self.queue, self.commits = queue, commits

    def dispatch(self, event: Event) -> list[object]:
        if not isinstance(event, self.QUEUED_EVENTS):
            return super().dispatch(event)
        return self.queued_dispatch(event)

    def queued_dispatch(self, event: Event) -> list[object]:
        for listener in self.background_listeners(type(event)):
            work = partial(listener.handle, event)
            self.commits.add(partial(copy_context().run, self.queue.add, work))
        return [listener.handle(event) for listener in self.answer_listeners(type(event))]
