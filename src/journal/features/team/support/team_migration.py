import time

from journal.config import Config
from journal.features.team.support.migration_plan import MigrationPlan
from journal.models.doc import Doc
from journal.features.docs.support.hub_move import HubMove
from journal.models.doc_edit_mode import DocEditMode
from journal.models.environment import Environment
from journal.models.model import Model
from journal.models.outgoing_change import KEPT_BY_ALL
from journal.repositories.doc_revisions import DocRevisions
from journal.repositories.docs import Docs
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.repositories.journal_backup import JournalBackup
from journal.repositories.scope import PROJECT
from journal.repositories.shared_tables import SharedTables
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.sync.migration_withdrawal import MigrationWithdrawal
from journal.sync.team_account import TeamAccount
from journal.sync.team_placement import TeamPlacement
from journal.sync.team_server_link import TeamServerLink
from sync_server.backup_answer import BackupAnswer

BACKUP_NAME = "journal-before-hub-%Y%m%d-%H%M%S.db"


class TeamMigration:
    """A team that synced everything moved to the hub by journal team migrate, once: its plan names the hub environment it makes, named as the team server names the team or else after the checkout, the project's documents and their revisions it moves into the hub, free to edit, and every row it withdraws, judged by where the hub places each once the documents are there. The run writes this journal and the team server to backups before anything changes, then makes the hub, moves the documents, queues the withdrawals and deletes here what another person keeps. A team that holds a hub is on it already, and a journal that has not learnt its team's key yet cannot place its rows; both are refused."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, environments: Environments, owners: EnvironmentOwners, withdrawal: MigrationWithdrawal, placement: TeamPlacement, docs: Docs, revisions: DocRevisions, hub_move: HubMove, tables: SharedTables, backups: JournalBackup, config: Config) -> None:
        self.account, self.link, self.environments, self.owners, self.withdrawal, self.placement = account, link, environments, owners, withdrawal, placement
        self.docs, self.revisions, self.hub_move, self.tables, self.backups, self.config = docs, revisions, hub_move, tables, backups, config

    def plan(self, actor: Actor) -> MigrationPlan:
        if self.environments.hubs():
            raise Rejection("this team is on the hub already: journal team migrate runs once")
        summary = self.link.summary(self.account.address())
        if self.account.team_key() != summary.key:
            raise Rejection("this journal has not learnt its team's key yet: let it sync once, then migrate")
        moved = tuple((row.table(), row.row_id) for row in self.moving())
        withdrawals = tuple(self.withdrawal.planned(actor.stamp, self.placement.moved({place: summary.key for place in moved})))
        keepers = {change.kept_by: self.owners.person_name(int(Actor.parse(change.kept_by).id)) for change in withdrawals if change.kept_by != KEPT_BY_ALL}
        return MigrationPlan(summary.key, summary.name or self.config.root.name, moved, withdrawals, tuple(environment.name for environment in self.environments.rows() if not environment.is_private()), keepers)

    def moving(self) -> list[Model]:
        return [row for doc in self.project_docs() for row in (doc, *self.revisions.document_revisions(doc))]

    def project_docs(self) -> list[Doc]:
        return self.docs.global_matching(environment_id=PROJECT)

    def run(self, actor: Actor) -> BackupAnswer:
        plan = self.plan(actor)
        self.backups.write(self.config.home / time.strftime(BACKUP_NAME))
        backup = self.link.backup()
        hub = self.environments.save(Environment.hub(plan.team_key, plan.hub), actor)
        for doc in self.project_docs():
            self.hub_move.put(doc, hub.row_id, DocEditMode.FREE, doc.owner, actor)
        self.withdrawal.withdraw(plan.withdrawals, actor)
        self.let_go(plan, actor)
        self.link.move_to_hub()
        self.account.record_on_hub()
        return backup

    def let_go(self, plan: MigrationPlan, actor: Actor) -> None:
        person = Actor.user(self.account.user_number()).stamp
        for change in plan.withdrawals:
            if change.kept_by not in (KEPT_BY_ALL, person):
                self.tables.rows(change.row_table).pulled_deletion(change.row, actor)
