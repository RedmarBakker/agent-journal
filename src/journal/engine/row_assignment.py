from journal.engine.state_machine import StateMachine
from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed


class RowAssignment(Listener[TaskClosed]):
    """The task assigner in force for each live agent is asked when a task closes, the one row event an assigner answers, once every other listener has heard it, on the same thread and in the same write, registered last, so a task that closes is let go and marked before the next one starts."""

    def __init__(self, machine: StateMachine) -> None:
        self.machine = machine

    def handle(self, event: TaskClosed) -> None:
        self.machine.row_assignments(event)
