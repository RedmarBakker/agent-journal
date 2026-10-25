from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.workers.support.test_turns import TestTurns
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks


class TestTurnTaskRelease(Listener[TaskClosed]):
    """A task closed takes out the waiting test turns, and stops the running test run, of the worker that held it."""

    __test__ = False

    def __init__(self, turns: TestTurns, tasks: Tasks) -> None:
        self.turns, self.tasks = turns, tasks

    def handle(self, event: TaskClosed) -> None:
        for worker in self.turns.holders():
            if event.task_id in self.tasks.holder_task_ids(Ref("workers", worker)):
                self.turns.release(worker)
