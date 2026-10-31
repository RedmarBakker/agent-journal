from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.organization.listeners.split_part_wake import SplitPartWake
from journal.models.task_state import TaskState
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class SplitCompletion(Listener[TaskClosed]):
    """Completes a plan task after all its Role parts close and at least one is complete."""

    def __init__(self, tasks: Tasks, time_source: TimeSource, seat_wake: SplitPartWake) -> None:
        self.tasks, self.time_source, self.seat_wake = tasks, time_source, seat_wake

    def handle(self, event: TaskClosed) -> None:
        part = self.tasks.find(event.task_id)
        parent = self.tasks.part_of_task(part)
        if parent is None or parent.state.is_closed():
            return
        parts = self.tasks.parts_of(parent)
        if not parts or any(not task.state.is_closed() for task in parts):
            return
        if any(task.state == TaskState.COMPLETED for task in parts):
            self.seat_wake.completed(event.task_id)
            outcome = f"all {len(parts)} parts merged"
            self.tasks.save(parent.completed(self.time_source.moment(), outcome), Actor.system())
