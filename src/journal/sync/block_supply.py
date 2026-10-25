from journal.repositories.id_blocks import IdBlocks
from journal.repositories.shared_tables import SharedTables
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink


class BlockSupply:
    """The row numbers this machine asks the team server for: a new block for each shared table running low, while it is in a team, from the home team's server or, bound to a further team's account, from that team's; a journal outside one numbers its rows itself."""

    def __init__(self, link: TeamServerLink, blocks: IdBlocks, tables: SharedTables, account: TeamAccount) -> None:
        self.link, self.blocks, self.tables, self.account = link, blocks, tables, account

    def bound(self, account: TeamAccount) -> "BlockSupply":
        return BlockSupply(self.link.bound(account), self.blocks, self.tables, account)

    def refill(self) -> None:
        if not self.account.is_joined():
            return
        wanted = [table for table in self.tables.names() if self.blocks.is_wanted(table, self.account.key)]
        if wanted:
            for grant in self.link.fetch_blocks(wanted).blocks:
                self.blocks.add(grant.row_table, grant.first, grant.last, self.account.key)
