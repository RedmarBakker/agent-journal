import time

from journal.config import Config
from journal.repositories.journal_backup import JournalBackup
from journal.repositories.links import Links
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.shared_tables import SharedTables
from journal.support.actor import Actor
from journal.sync.team_account import TeamAccount
from journal.sync.team_change import TeamChange

BACKUP_NAME = "journal-before-withdrawal-%Y%m%d-%H%M%S.db"


class IncomingChanges:
    """Writes the changes the team server passes on into this journal, each through its table's repository, so no listener that acts on a local write runs. A row withdrawn from the team is kept as this machine has it when it is every journal's to keep or this journal's person's, and deleted otherwise, once this journal is written to a backup file beside it, the first of any second kept, its links left to their own withdrawals so no deletion of them goes back to the team. A column this machine does not know yet is left out, and a field this machine's own queue still holds is stored as this machine has it."""

    def __init__(self, tables: SharedTables, outgoing: OutgoingChanges, links: Links, account: TeamAccount, backups: JournalBackup, config: Config) -> None:
        self.tables, self.outgoing, self.links, self.account, self.backups, self.config = tables, outgoing, links, account, backups, config

    def apply(self, changes: list[TeamChange]) -> None:
        applied = [change for change in changes if self.tables.has(change.row_table) and not self.is_kept(change)]
        backup = self.config.home / time.strftime(BACKUP_NAME)
        if any(change.is_withdrawal() for change in applied) and not backup.exists():
            self.backups.write(backup)
        for change in applied:
            self.applied(change)

    def is_kept(self, change: TeamChange) -> bool:
        return change.is_withdrawal() and change.is_kept_by(Actor.user(self.account.user_number()))

    def applied(self, change: TeamChange) -> None:
        if change.is_withdrawal():
            self.removed(change)
        elif change.is_deletion():
            self.deleted(change)
        elif change.is_creation():
            self.tables.rows(change.row_table).pulled_creation(change.row, self.unqueued(change), change.actor())
        else:
            self.tables.rows(change.row_table).pulled_update(change.row, self.unqueued(change), change.actor())

    def unqueued(self, change: TeamChange) -> dict:
        return change.fields_without(self.outgoing.queued_fields(change.row_table, change.row))

    def deleted(self, change: TeamChange) -> None:
        for row in self.removed(change):
            self.links.remove_links(row, change.actor())

    def removed(self, change: TeamChange) -> list:
        self.outgoing.dropped(change.row_table, change.row, change.actor())
        return self.tables.rows(change.row_table).pulled_deletion(change.row, change.actor())
