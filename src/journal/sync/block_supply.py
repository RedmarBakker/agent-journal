from journal.repositories.id_blocks import IdBlocks
from journal.repositories.shared_tables import SharedTables
from journal.sync.team_server_link import TeamServerLink


class BlockSupply:
    """The row numbers this machine asks the team server for: a new block for each shared table running low."""

    def __init__(self, link: TeamServerLink, blocks: IdBlocks, tables: SharedTables) -> None:
        self.link, self.blocks, self.tables = link, blocks, tables

    def refill(self) -> None:
        wanted = [table for table in self.tables.names() if self.blocks.is_wanted(table)]
        if wanted:
            for grant in self.link.fetch_blocks(wanted).blocks:
                self.blocks.add(grant.row_table, grant.first, grant.last)
