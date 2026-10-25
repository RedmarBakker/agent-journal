from journal.events.listener import Listener
from journal.events.models.synced_update import SyncedUpdate
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.plan import Plan
from journal.models.task import Task
from journal.sync.hub_drives import HubDrives


class DrivenRowClosures(Listener[SyncedUpdate]):
    """A hub plan or task driven here that another journal finished or cancelled ends its drive here, heard after the tasks feature, listed before plans, has passed the closure to the environment driving it."""

    def __init__(self, drives: HubDrives, bindings: PlanBindings) -> None:
        self.drives, self.bindings = drives, bindings

    def handle(self, event: SyncedUpdate) -> None:
        if self.is_driven_closure(event):
            self.bindings.end(event.model, f"{self.drives.doer(event.actor)} marked it {event.model.state.value} on another journal", event.actor)

    def is_driven_closure(self, event: SyncedUpdate) -> bool:
        return isinstance(event.model, (Task, Plan)) and event.model.state.is_closed() and not event.previous.state.is_closed() and bool(self.bindings.environment_id(event.model))
