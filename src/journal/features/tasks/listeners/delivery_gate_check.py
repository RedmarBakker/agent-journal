from journal.events.listener import Listener
from journal.events.models.saving import Saving
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.task_dependencies import TaskDependencies


class DeliveryGateCheck(Listener[Saving]):
    """A delivery gate task completes only after its target has accepted domain delivery evidence."""

    def __init__(self, dependencies: TaskDependencies) -> None:
        self.dependencies = dependencies

    def handle(self, event: Saving) -> None:
        task = event.model
        if not isinstance(task, Task) or task.state != TaskState.COMPLETED or task.is_new:
            return
        if self.dependencies.tasks.find(task.row_id).state != TaskState.COMPLETED:
            self.dependencies.require_delivery_evidence(task)
