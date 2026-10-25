from journal.models.all_models import AllModels
from journal.models.environment import Environment
from journal.models.model import Model
from journal.models.outgoing_change import OutgoingChange
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.links import Links
from journal.repositories.shared_tables import SharedTables
from journal.support.actor import Actor
from journal.sync.setting_scopes import SettingScopes
from journal.sync.team_account import TeamAccount


class EnvironmentWithdrawal:
    """The withdrawals that take one environment off the team, kept by its owner, or by this journal's person when it has none: its contents, the links touching its rows and then every team row in it, and after them the links touching the environment itself and its own row."""

    def __init__(self, account: TeamAccount, tables: SharedTables, links: Links, owners: EnvironmentOwners, scopes: SettingScopes) -> None:
        self.account, self.tables, self.links, self.owners, self.scopes = account, tables, links, owners, scopes

    def changes(self, environment_id: int, writer: str) -> list[OutgoingChange]:
        environment = self.tables.rows(Environment.table()).find(environment_id)
        return [*self.content_changes(environment_id, writer), *(OutgoingChange.withdrawal(row, writer, self.keeper(environment_id)) for row in [*self.links.touching_any([environment]), environment])]

    def content_changes(self, environment_id: int, writer: str) -> list[OutgoingChange]:
        rows = self.team_rows(environment_id)
        return [OutgoingChange.withdrawal(row, writer, self.keeper(environment_id)) for row in [*self.links.touching_any(rows), *rows]]

    def keeper(self, environment_id: int) -> str:
        return Actor.user(self.owners.owner_number(environment_id) or self.account.user_number()).stamp

    def team_rows(self, environment_id: int) -> list[Model]:
        return [row for model in AllModels.SCOPED if model.shared for row in self.tables.rows(model.table()).all_matching(environment_id=environment_id) if self.scopes.is_team_row(row)]
