from journal.events.listener import Listener
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.features.workers.support.test_turns import TestTurns
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState

ENDED = (WorkerState.STOPPED, WorkerState.REPORTED, WorkerState.MERGED, WorkerState.RELEASED, WorkerState.UNFINISHED)


class TestTurnRelease(Listener[ModelEvent]):
    """A worker that ends, is stopped, retired, released or merged takes out its waiting test turns and has its running test run stopped, which gives the place on to the next turn."""

    __test__ = False

    def __init__(self, turns: TestTurns) -> None:
        self.turns = turns

    def handle(self, event: ModelEvent) -> None:
        if isinstance(event, Updated) and isinstance(event.model, Worker) and (event.model.state in ENDED or event.model.adopted):
            self.turns.release(event.model.row_id)
