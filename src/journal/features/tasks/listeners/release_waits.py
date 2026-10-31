from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_reopened import TaskReopened
from journal.events.rows.task_started import TaskStarted
from journal.features.tasks.support.waits import Waits
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor


class ReleaseWaits(Listener[RowEvent]):
    """A task open again or taken up again waits on nothing: its wait links go and the checks its block made are deleted."""

    def __init__(self, tasks: Tasks, waits: Waits) -> None:
        self.tasks, self.waits = tasks, waits

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, (TaskReopened, TaskStarted)):
            self.waits.released(self.tasks.find(event.task_id), Actor.system())
