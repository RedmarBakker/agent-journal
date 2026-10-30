from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.repositories.scope import Scope
from journal.repositories.task_outcomes import TaskOutcomes


class TaskOutcomeEvents(Listener[RowEvent]):
    """Records task and worker lifecycle facts in the task outcome ledger."""

    def __init__(self, outcomes: TaskOutcomes, scope: Scope) -> None:
        self.outcomes, self.scope = outcomes, scope

    def handle(self, event: RowEvent) -> None:
        with self.scope.environment(event.environment_id):
            self.outcomes.record_row_event(event)
