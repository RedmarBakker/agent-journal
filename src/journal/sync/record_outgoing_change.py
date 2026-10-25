from functools import partial
from typing import Callable

from journal.db.schema import Schema
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.events.models.deleted import Deleted
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.models.all_models import AllModels
from journal.models.environment import Environment
from journal.models.model import Model
from journal.models.outgoing_change import CREATED, DELETED, UPDATED, OutgoingChange
from journal.repositories.links import Links
from journal.support.actor import Actor
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.shared_tables import SharedTables
from journal.sync.row_renumbering import RowRenumbering
from journal.sync.team_accounts import TeamAccounts
from journal.sync.team_account import TeamAccount
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.sync.team_placement import TeamPlacement

ACTIONS = {Created: CREATED, Updated: UPDATED, Deleted: DELETED}
STAMP_COLUMNS = ("updated_at", "updater")


class RecordOutgoingChange(Listener[ModelEvent]):
    """Every write to a shared row is queued for the team server in the write's own transaction, once this journal has joined a team and only when TeamPlacement sends it: a creation with all its columns, an update with the ones it changed, a deletion with none; a row an update moves into the team, which the server has never had, is sent whole as a creation, a change to a further team carrying this person's account in that team in place of the home team's, an environment with every row in it, its whole history, and every link that now joins one of them to a row of the team, each first moved into the team's row numbers when the team server never handed this machine its number, as for a row made before joining, and one an update takes out of it is withdrawn with its links, kept by whoever took it."""

    def __init__(self, changes: OutgoingChanges, account: TeamAccount, placement: TeamPlacement, links: Links, tables: SharedTables, renumbering: RowRenumbering, accounts: TeamAccounts, hooks: ServiceHooks) -> None:
        self.changes, self.account, self.placement, self.links, self.tables, self.renumbering, self.hooks = changes, account, placement, links, tables, renumbering, hooks
        self.accounts = accounts

    def handle(self, event: ModelEvent) -> None:
        action = ACTIONS.get(type(event))
        if action == UPDATED and self.account.is_joined() and event.previous is not None and self.placement.is_sent(event.previous) and not self.placement.is_sent(event.model):
            self.left(event)
            return
        if action is None or not self.account.is_joined() or not self.placement.is_sent(event.model):
            return
        if action == UPDATED and event.previous is not None and not self.placement.is_sent(event.previous):
            self.entered(event)
            return
        self.queued(event.model, action, self.names(event, action), event.actor)

    def left(self, event: Updated) -> None:
        for row in (event.model, *self.links.link_rows(event.model)):
            self.changes.queued(OutgoingChange.withdrawal(row, event.actor.stamp, event.actor.stamp), event.actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))

    def entered(self, event: Updated) -> None:
        rows = [event.model, *self.contents(event.model)]
        rows = [*rows, *(link for link in self.links.touching_any(rows) if self.placement.is_sent(link))]
        refs = self.renumbering.into_team(rows)
        if refs:
            rows = [self.tables.rows(row.table()).numbered([refs.get(row.table(), {}).get(row.row_id, row.row_id)])[0] for row in rows]
        for row in rows:
            self.queued(row, CREATED, None, event.actor)

    def contents(self, row: Model) -> list[Model]:
        if not isinstance(row, Environment):
            return []
        return [stored for model in AllModels.SCOPED if model.shared for stored in self.tables.rows(model.table()).all_matching(environment_id=row.row_id) if self.placement.is_sent(stored)]

    def queued(self, row: Model, action: str, names: tuple[str, ...] | None, actor: Actor) -> None:
        fields = Schema.team_values(row.team_ready(self.account.prefix()), names if action != CREATED else None)
        if names is not None and not set(fields) - set(STAMP_COLUMNS) and action != DELETED:
            return
        updated_at, team_key = row.updated_at.timestamp(), self.placement.team_key(row)
        person = self.team_person(team_key)
        fields = {name: person(value) if isinstance(value, str) else value for name, value in fields.items()}
        self.changes.queued(OutgoingChange(row_table=row.table(), row=row.row_id, action=action, fields=fields, changed_at={name: updated_at for name in fields}, writer=person(actor.stamp), team_key=team_key), actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))

    def team_person(self, team_key: str) -> Callable[[str], str]:
        team = self.accounts.keyed(team_key)
        home, theirs = Actor.user(self.account.user_number()).stamp, Actor.user(team.user_number()).stamp
        return (lambda stamp: theirs if stamp == home else stamp) if team.key else (lambda stamp: stamp)

    @staticmethod
    def names(event: ModelEvent, action: str) -> tuple[str, ...] | None:
        if action == DELETED:
            return ()
        if action == UPDATED:
            return (*event.changed(), *STAMP_COLUMNS)
        return None
