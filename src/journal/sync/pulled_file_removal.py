from journal.events.listener import Listener
from journal.events.models.synced_deletion import SyncedDeletion
from journal.sync.attachments import Attachments


class PulledFileRemoval(Listener[SyncedDeletion]):
    """The files of a message or dump another machine deleted or withdrew from the team are removed from this machine's folder with it."""

    def __init__(self, attachments: Attachments) -> None:
        self.attachments = attachments

    def handle(self, event: SyncedDeletion) -> None:
        self.attachments.removed(event.model.table(), event.model.row_id)
