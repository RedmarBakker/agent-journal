from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.memory.support.memory_ends import MemoryEnds
from journal.models.task_state import TaskState
from journal.repositories.tasks import Tasks

ENDING_STATES = (TaskState.COMPLETED, TaskState.CANCELLED)


class MemoryTaskEnd(Listener[TaskClosed]):
    """A task done or cancelled removes the memories that end with it; a task only paused leaves them."""

    def __init__(self, ends: MemoryEnds, tasks: Tasks) -> None:
        self.ends, self.tasks = ends, tasks

    def handle(self, event: TaskClosed) -> None:
        if self.tasks.find(event.task_id).state in ENDING_STATES:
            self.ends.row_closed(event.environment_id, f"tasks:{event.task_id}", event.time)
