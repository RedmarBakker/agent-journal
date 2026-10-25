from functools import partial

from journal.models.environment import Environment
from journal.models.model import Model
from journal.models.outgoing_change import KEPT_BY_ALL, OutgoingChange
from journal.models.scoped import Scoped
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.shared_tables import SharedTables
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.support.actor import Actor
from journal.sync.environment_withdrawal import EnvironmentWithdrawal
from journal.sync.setting_scopes import SettingScopes
from journal.sync.team_placement import TeamPlacement


class MigrationWithdrawal:
    """The withdrawals the move to the hub makes, of every row the team synced that the hub's placement puts in no team: the rows of each environment its owner has not shared, and the links that touch them, kept by its owner; every other one, those environments' own rows and rules, templates and the rest of what belongs to no environment among them, kept by all."""

    def __init__(self, changes: OutgoingChanges, tables: SharedTables, environments: EnvironmentWithdrawal, scopes: SettingScopes, hooks: ServiceHooks) -> None:
        self.changes, self.tables, self.environments, self.scopes, self.hooks = changes, tables, environments, scopes, hooks

    def planned(self, writer: str, placement: TeamPlacement) -> list[OutgoingChange]:
        environments = self.tables.rows(Environment.table()).rows()
        owned = [change for environment in environments if environment.is_private() for change in self.environments.content_changes(environment.row_id, writer)]
        taken = {(change.row_table, change.row) for change in owned}
        placed = [environment.row_id for environment in environments]
        return [*owned, *(OutgoingChange.withdrawal(row, writer, KEPT_BY_ALL) for row in self.unplaced(placement, placed) if (row.table(), row.row_id) not in taken)]

    def unplaced(self, placement: TeamPlacement, placed: list[int]) -> list[Model]:
        return [row for table in self.tables.names() for row in self.outside(table, placed) if self.scopes.is_team_row(row) and not placement.is_team_row(row)]

    def outside(self, table: str, placed: list[int]) -> list[Model]:
        rows = self.tables.rows(table)
        return rows.selected(rows.query().filter_unlisted("environment_id", placed).order("id")) if issubclass(rows.model, Scoped) else rows.rows()

    def withdraw(self, withdrawals: tuple[OutgoingChange, ...], actor: Actor) -> None:
        for change in withdrawals:
            self.changes.queued(change, actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))
