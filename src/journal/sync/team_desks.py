from journal.repositories.outgoing_changes import OutgoingChanges
from journal.sync.block_supply import BlockSupply
from journal.sync.incoming_changes import IncomingChanges
from journal.sync.journal_copy import JournalCopy
from journal.sync.rejected_edits import RejectedEdits
from journal.sync.team_accounts import TeamAccounts
from journal.sync.team_desk import TeamDesk
from journal.sync.team_server_link import TeamServerLink


class TeamDesks:
    """The desk of each team this journal joined beside its home team, one per team, made the first time that team's carrier comes and kept, each bound to that team's account and server."""

    def __init__(self, accounts: TeamAccounts, link: TeamServerLink, outgoing: OutgoingChanges, incoming: IncomingChanges, rejected: RejectedEdits, copy: JournalCopy, supply: BlockSupply) -> None:
        self.accounts, self.link, self.outgoing, self.incoming, self.rejected, self.copy, self.supply = accounts, link, outgoing, incoming, rejected, copy, supply
        self.desks: dict[str, TeamDesk] = {}

    def further_keys(self) -> list[str]:
        return [account.key for account in self.accounts.accounts() if account.key]

    def desk(self, team_key: str) -> TeamDesk:
        if team_key not in self.desks:
            account = self.accounts.keyed(team_key)
            self.desks[team_key] = TeamDesk(account, self.link.bound(account), self.outgoing, self.incoming, self.rejected, self.copy, self.supply.bound(account))
        return self.desks[team_key]
