from functools import partial

from journal.events.listener import Listener
from journal.events.rows.environment_unshared import EnvironmentUnshared
from journal.models.all_models import AllModels
from journal.models.environment import Environment
from journal.models.model import Model
from journal.models.outgoing_change import WITHDRAWN, OutgoingChange
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.links import Links
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.shared_tables import SharedTables
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.support.actor import Actor
from journal.sync.setting_scopes import SettingScopes
from journal.sync.team_account import TeamAccount


class RecordWithdrawal(Listener[EnvironmentUnshared]):
    """An environment taken back from the team is queued for the team server as withdrawn, kept by its owner: the links touching its rows first, then every team row in it, then its own row, so the server and every colleague's journal let go of them and the owner's journals keep theirs."""

    def __init__(self, changes: OutgoingChanges, account: TeamAccount, tables: SharedTables, links: Links, owners: EnvironmentOwners, scopes: SettingScopes, hooks: ServiceHooks) -> None:
        self.changes, self.account, self.tables, self.links, self.owners, self.scopes, self.hooks = changes, account, tables, links, owners, scopes, hooks

    def handle(self, event: EnvironmentUnshared) -> None:
        if not self.account.is_joined():
            return
        rows = [*self.team_rows(event.environment_id), self.tables.rows(Environment.table()).find(event.environment_id)]
        keeper = Actor.user(self.owners.owner_number(event.environment_id) or self.account.user_number()).stamp
        actor = Actor.parse(event.actor)
        for row in [*self.links.touching_any(rows), *rows]:
            self.changes.queued(OutgoingChange(row_table=row.table(), row=row.row_id, action=WITHDRAWN, fields={}, changed_at={}, writer=actor.stamp, kept_by=keeper), actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))

    def team_rows(self, environment_id: int) -> list[Model]:
        return [row for model in AllModels.SCOPED if model.shared for row in self.tables.rows(model.table()).all_matching(environment_id=environment_id) if self.scopes.is_team_row(row)]
