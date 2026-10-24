from journal.events.listener import Listener
from journal.events.models.number_request import NumberRequest
from journal.repositories.id_blocks import IdBlocks
from journal.repositories.number_shortage import NumberShortage
from journal.sync.block_supply import BlockSupply
from journal.sync.team_account import TeamAccount


class BlockNumbers(Listener[NumberRequest]):
    """A new row of a shared model, or of one sharing a shared model's table, takes its number from this machine's blocks of that model once the journal has joined a team, so no two machines give one number, asking the team server for more there and then when a table has none left; otherwise SQLite numbers it."""

    def __init__(self, blocks: IdBlocks, account: TeamAccount, supply: BlockSupply) -> None:
        self.blocks, self.account, self.supply = blocks, account, supply

    def handle(self, event: NumberRequest) -> int:
        pool = event.model.number_pool()
        if pool is None or not self.account.is_joined():
            return 0
        if not self.blocks.has_numbers(pool):
            self.refilled(pool)
        return self.blocks.next_id(pool)

    def refilled(self, table: str) -> None:
        try:
            self.supply.refill()
        except OSError as unreachable:
            raise NumberShortage(f"every row number this machine holds for {table} is used, and the team server could not be reached for more: {unreachable}") from unreachable
