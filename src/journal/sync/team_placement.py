from journal.models.environment import UNKNOWN_TEAM_KEY, Environment
from journal.models.link import Link
from journal.models.model import Model
from journal.models.scoped import Scoped
from journal.models.setting import Setting
from journal.models.support.ref import Ref
from journal.models.user import User
from journal.features.plans.support.plan_bindings import ENDED_LINK
from journal.repositories.scope import BOUND_LINK, PROJECT
from journal.repositories.shared_tables import SharedTables
from journal.sync.setting_scopes import SettingScopes
from journal.sync.team_account import TeamAccount

NO_TEAM = ""
# the links that say what this machine does with a hub row, never the team's: an environment's binding of a hub plan or task, and its drive ended
MACHINE_LINKS = (BOUND_LINK, ENDED_LINK)


class TeamPlacement:
    """The team a row belongs to, by its key, or none: an environment when it is a hub, a session or one its owner shares, each with its team; a row of an environment with that environment, but for a row it withholds, such as a local copy of a hub document; a link only when both its ends are in one team, and never a binding of a hub row or its ended drive, which are this machine's alone; a person in the home team; a setting of the team's scope in the home team when it is the project's, else with its environment; every other row, rules and templates among them, in none; and whether a row is sent to the team server, and to which team's, the home team's every row it sends but a further team's, a further team's only its own: a row of a team at all on a team on the hub, as on a team not yet moved there every shared row but a setting of one person or machine. A placement moved by rows and the teams they are going to answers as if they were there already."""

    def __init__(self, tables: SharedTables, scopes: SettingScopes, account: TeamAccount) -> None:
        self.tables, self.scopes, self.account = tables, scopes, account
        self.placements = {Environment: self.environment_team, Link: self.link_team, User: self.user_team, Setting: self.setting_team}
        self.moves: dict[tuple[str, int], str] = {}

    def moved(self, moves: dict[tuple[str, int], str]) -> "TeamPlacement":
        placement = TeamPlacement(self.tables, self.scopes, self.account)
        placement.moves = moves
        return placement

    def team_key(self, row: Model) -> str:
        if not row.shared or row.is_withheld():
            return NO_TEAM
        if (row.table(), row.id) in self.moves:
            return self.moves[(row.table(), row.id)]
        placed = self.placements.get(type(row))
        if placed:
            return placed(row)
        return self.environment_key(row.environment_id) if isinstance(row, Scoped) else NO_TEAM

    def is_team_row(self, row: Model) -> bool:
        return bool(self.team_key(row))

    def is_sent(self, row: Model) -> bool:
        return self.is_team_row(row) if self.account.is_on_hub() else self.scopes.is_team_row(row)

    def is_sent_to(self, row: Model, account: TeamAccount) -> bool:
        if account.key:
            return self.team_key(row) == account.key
        return self.is_sent(row) and self.team_key(row) in (NO_TEAM, self.account.team_key(), UNKNOWN_TEAM_KEY)

    @staticmethod
    def environment_team(environment: Environment) -> str:
        return NO_TEAM if environment.is_private() else environment.team_key

    def link_team(self, link: Link) -> str:
        if link.kind in MACHINE_LINKS:
            return NO_TEAM
        ends = {self.ref_key(link.source), self.ref_key(link.target)}
        return ends.pop() if len(ends) == 1 else NO_TEAM

    def user_team(self, user: User) -> str:
        return self.account.team_key()

    def setting_team(self, setting: Setting) -> str:
        if not self.scopes.is_team(setting.key):
            return NO_TEAM
        return self.account.team_key() if setting.environment_id == PROJECT else self.environment_key(setting.environment_id)

    def environment_key(self, environment_id: int) -> str:
        environments = self.tables.rows(Environment.table()).numbered([environment_id]) if environment_id != PROJECT else []
        return self.environment_team(environments[0]) if environments else NO_TEAM

    def ref_key(self, ref: Ref) -> str:
        rows = self.tables.rows(ref.type).numbered([ref.id]) if self.tables.has(ref.type) else []
        return self.team_key(rows[0]) if rows else NO_TEAM
