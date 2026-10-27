from journal.events.listener import Listener
from journal.events.models.deleting import Deleting
from journal.events.models.model_event import ModelEvent
from journal.events.models.saving import Saving
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.plan import Plan
from journal.models.task import Task
from journal.support.rejection import Rejection
from journal.support.row_labels import RowLabels

GUARDED = (Saving, Deleting)
REFUSAL = "{name} is driven from here no longer, so it is not written here: journal {noun} drive {n} takes it again once it is free"


class EndedDriveWriteGuard(Listener[ModelEvent]):
    """A save or deletion of a hub plan or task whose drive ended on this machine is refused before it is made, until the row is driven from here again."""

    blocking = True

    def __init__(self, bindings: PlanBindings, labels: RowLabels) -> None:
        self.bindings, self.labels = bindings, labels

    def handle(self, event: ModelEvent) -> None:
        row = event.model
        if isinstance(event, GUARDED) and isinstance(row, (Task, Plan)) and not row.is_new and self.bindings.is_ended(row):
            noun = type(row).__name__.lower()
            raise Rejection(REFUSAL.format(name=self.labels.name(noun, row), noun=noun, n=row.row_id))
