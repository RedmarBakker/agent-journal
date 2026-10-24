from journal.repositories.id_blocks import IdBlocks
from journal.repositories.shared_tables import SharedTables
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink


class BlockSupply:
    """The row numbers this machine asks the team server for: a new block for each shared table running low, while it is in a team; a journal outside one numbers its rows itself."""

    def __init__(self, link: TeamServerLink, blocks: IdBlocks, tables: SharedTables, account: TeamAccount) -> None:
        self.link, self.blocks, self.tables, self.account = link, blocks, tables, account

    def refill(self) -> None:
        if not self.account.is_joined():
            return
        wanted = [table for table in self.tables.names() if self.blocks.is_wanted(table)]
        if wanted:
            for grant in self.link.fetch_blocks(wanted).blocks:
                self.blocks.add(grant.row_table, grant.first, grant.last)
