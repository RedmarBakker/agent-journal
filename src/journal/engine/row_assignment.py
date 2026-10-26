from journal.engine.state_machine import StateMachine
from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent


class RowAssignment(Listener[RowEvent]):
    """The task assigner in force for each live agent is asked about a row event once every other listener has heard it, on the same thread and in the same write, registered last, so a task that closes is let go and marked before the next one starts."""

    def __init__(self, machine: StateMachine) -> None:
        self.machine = machine

    def handle(self, event: RowEvent) -> None:
        self.machine.row_assignments(event)
