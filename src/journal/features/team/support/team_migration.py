from journal.config import Config
from journal.features.team.support.migration_plan import MigrationPlan
from journal.models.environment import Environment
from journal.models.outgoing_change import KEPT_BY_ALL
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.sync.migration_withdrawal import MigrationWithdrawal
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink
from sync_server.backup_answer import BackupAnswer


class TeamMigration:
    """A team that synced everything moved to the hub by journal team migrate, once: its plan names the hub environment it makes, named as the team server names the team or else after the checkout, and every row it withdraws; the run has the team server write its backup before anything changes, then makes the hub and queues the withdrawals. A team that holds a hub is on it already, and is refused."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, environments: Environments, owners: EnvironmentOwners, withdrawal: MigrationWithdrawal, config: Config) -> None:
        self.account, self.link, self.environments, self.owners, self.withdrawal, self.config = account, link, environments, owners, withdrawal, config

    def plan(self, actor: Actor) -> MigrationPlan:
        if self.environments.hubs():
            raise Rejection("this team is on the hub already: journal team migrate runs once")
        summary = self.link.summary(self.account.address())
        withdrawals = tuple(self.withdrawal.planned(actor.stamp))
        keepers = {change.kept_by: self.owners.person_name(int(Actor.parse(change.kept_by).id)) for change in withdrawals if change.kept_by != KEPT_BY_ALL}
        return MigrationPlan(summary.key, summary.name or self.config.root.name, withdrawals, tuple(environment.name for environment in self.environments.rows() if not environment.is_private()), keepers)

    def run(self, actor: Actor) -> BackupAnswer:
        plan = self.plan(actor)
        backup = self.link.backup()
        self.environments.save(Environment.hub(plan.team_key, plan.hub), actor)
        self.withdrawal.withdraw(actor)
        return backup
