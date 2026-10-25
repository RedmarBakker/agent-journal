from functools import partial

from journal.events.listener import Listener
from journal.events.models.purged import Purged
from journal.models.outgoing_change import DELETED, OutgoingChange
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.sync.team_account import TeamAccount
from journal.sync.team_placement import TeamPlacement
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks


class RecordPurge(Listener[Purged]):
    """Every row deleted together with others that TeamPlacement sends to the team is queued for the team server as a deletion of its own, so the server's copy keeps no row this machine removed."""

    def __init__(self, changes: OutgoingChanges, account: TeamAccount, placement: TeamPlacement, hooks: ServiceHooks) -> None:
        self.changes, self.account, self.placement, self.hooks = changes, account, placement, hooks

    def handle(self, event: Purged) -> None:
        if not self.account.is_joined():
            return
        for row in event.rows:
            if self.placement.is_sent(row):
                self.changes.queued(OutgoingChange(row_table=event.model.table(), row=row.row_id, action=DELETED, fields={}, changed_at={}, writer=event.actor.stamp), event.actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))
