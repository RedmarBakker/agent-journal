from journal.engine.state_machine import StateMachine
from journal.events.listener import Listener
from journal.events.rows.task_assignment_opportunity import TaskAssignmentOpportunity


class RowAssignment(Listener[TaskAssignmentOpportunity]):
    """The task assigner is asked at an explicit safe assignment opportunity, after row listeners have updated agent state."""

    def __init__(self, machine: StateMachine) -> None:
        self.machine = machine

    def handle(self, event: TaskAssignmentOpportunity) -> None:
        self.machine.row_assignments(event)
