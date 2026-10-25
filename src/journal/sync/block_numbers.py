from journal.events.listener import Listener
from journal.events.models.number_request import NumberRequest
from journal.repositories.id_blocks import IdBlocks
from journal.repositories.number_shortage import NumberShortage
from journal.sync.block_supply import BlockSupply
from journal.sync.team_account import TeamAccount
from journal.sync.team_accounts import TeamAccounts
from journal.sync.team_placement import TeamPlacement


class BlockNumbers(Listener[NumberRequest]):
    """A new row of a shared model, or of one sharing a shared model's table, takes its number from this machine's blocks of that model once the journal has joined a team, the blocks of the team the row belongs to when that is a further team and else the home team's, so no two machines give one number, asking the team server for more there and then when a table has none left; otherwise SQLite numbers it."""

    def __init__(self, blocks: IdBlocks, account: TeamAccount, supply: BlockSupply, placement: TeamPlacement, accounts: TeamAccounts) -> None:
        self.blocks, self.account, self.supply, self.placement, self.accounts = blocks, account, supply, placement, accounts

    def handle(self, event: NumberRequest) -> int:
        pool = event.model.number_pool()
        if pool is None or not self.account.is_joined():
            return 0
        team = self.accounts.keyed(self.placement.team_key(event.model))
        if not self.blocks.has_numbers(pool, team.key):
            self.refilled(pool, team)
        return self.blocks.next_id(pool, team.key)

    def refilled(self, table: str, team: TeamAccount) -> None:
        try:
            (self.supply.bound(team) if team.key else self.supply).refill()
        except OSError as unreachable:
            raise NumberShortage(f"every row number this machine holds for {table} is used, and the team server could not be reached for more: {unreachable}") from unreachable
