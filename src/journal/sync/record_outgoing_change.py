from functools import partial

from journal.db.schema import Schema
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.events.models.deleted import Deleted
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.models.model import Model
from journal.models.outgoing_change import CREATED, DELETED, UPDATED, OutgoingChange
from journal.repositories.links import Links
from journal.support.actor import Actor
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.sync.team_account import TeamAccount
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.sync.team_placement import TeamPlacement

ACTIONS = {Created: CREATED, Updated: UPDATED, Deleted: DELETED}
STAMP_COLUMNS = ("updated_at", "updater")


class RecordOutgoingChange(Listener[ModelEvent]):
    """Every write to a shared row is queued for the team server in the write's own transaction, once this journal has joined a team and only when TeamPlacement sends it: a creation with all its columns, an update with the ones it changed, a deletion with none; a row an update moves into the team, which the server has never had, is sent whole as a creation, with every link that now joins it to a row of the team."""

    def __init__(self, changes: OutgoingChanges, account: TeamAccount, placement: TeamPlacement, links: Links, hooks: ServiceHooks) -> None:
        self.changes, self.account, self.placement, self.links, self.hooks = changes, account, placement, links, hooks

    def handle(self, event: ModelEvent) -> None:
        action = ACTIONS.get(type(event))
        if action is None or not self.account.is_joined() or not self.placement.is_sent(event.model):
            return
        if action == UPDATED and event.previous is not None and not self.placement.is_sent(event.previous):
            self.entered(event)
            return
        self.queued(event.model, action, self.names(event, action), event.actor)

    def entered(self, event: Updated) -> None:
        for row in (event.model, *(link for link in self.links.link_rows(event.model) if self.placement.is_sent(link))):
            self.queued(row, CREATED, None, event.actor)

    def queued(self, row: Model, action: str, names: tuple[str, ...] | None, actor: Actor) -> None:
        fields = Schema.team_values(row.team_ready(self.account.prefix()), names if action != CREATED else None)
        if names is not None and not set(fields) - set(STAMP_COLUMNS) and action != DELETED:
            return
        updated_at = row.updated_at.timestamp()
        self.changes.queued(OutgoingChange(row_table=row.table(), row=row.row_id, action=action, fields=fields, changed_at={name: updated_at for name in fields}, writer=actor.stamp), actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))

    @staticmethod
    def names(event: ModelEvent, action: str) -> tuple[str, ...] | None:
        if action == DELETED:
            return ()
        if action == UPDATED:
            return (*event.changed(), *STAMP_COLUMNS)
        return None
