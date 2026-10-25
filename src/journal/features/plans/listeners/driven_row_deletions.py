from journal.events.listener import Listener
from journal.events.models.synced_deletion import SyncedDeletion
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.plan import Plan
from journal.models.task import Task
from journal.sync.hub_drives import HubDrives


class DrivenRowDeletions(Listener[SyncedDeletion]):
    """A hub plan or task driven here that another journal deleted ends its drive here, before its links go."""

    def __init__(self, drives: HubDrives, bindings: PlanBindings) -> None:
        self.drives, self.bindings = drives, bindings

    def handle(self, event: SyncedDeletion) -> None:
        if isinstance(event.model, (Task, Plan)) and self.bindings.environment_id(event.model):
            self.bindings.end(event.model, f"{self.drives.doer(event.actor)} deleted it on another journal", event.actor)
