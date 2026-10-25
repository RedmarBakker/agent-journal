from journal.models.id_block import IdBlock
from journal.repositories.repository import Repository
from journal.support.actor import Actor
from journal.repositories.number_shortage import NumberShortage

RESERVE_SHARE = 5


class IdBlocks(Repository[IdBlock]):
    """The row numbers each team server handed this machine per table, the home team's under no key and a further team's under its own, oldest block first: a used block is kept, so the numbers this machine has given are known as the team's, and a table wants a new block once fewer numbers are left than a block and a fifth of one."""

    model = IdBlock

    def add(self, table: str, first: int, last: int, team_key: str = "") -> IdBlock:
        return self.save(IdBlock(row_table=table, first_number=first, last_number=last, next_number=first, team_key=team_key), Actor.system())

    def next_id(self, table: str, team_key: str = "") -> int:
        numbers = self.taken(table, 1, team_key)
        if not numbers:
            raise NumberShortage(f"every row number this machine holds for {table} is used, and the team server gave no more")
        return numbers[0]

    def taken(self, table: str, count: int, team_key: str = "") -> list[int]:
        numbers = []
        for block in self.open_blocks(table, team_key):
            if len(numbers) == count:
                break
            share = min(count - len(numbers), block.spare_count())
            numbers.extend(range(block.next_number, block.next_number + share))
            self.save(block.past(share), Actor.system())
        return numbers

    def open_blocks(self, table: str, team_key: str = "") -> list[IdBlock]:
        return [block for block in self.all_matching(row_table=table, team_key=team_key) if block.spare_count() > 0]

    def is_given(self, table: str, number: int) -> bool:
        return any(block.first_number <= number < block.next_number for block in self.all_matching(row_table=table))

    def clear(self) -> None:
        self.purged_rows(IdBlock, self.query(), Actor.system())

    def has_numbers(self, table: str, team_key: str = "") -> bool:
        return bool(self.open_blocks(table, team_key))

    def is_wanted(self, table: str, team_key: str = "") -> bool:
        blocks = self.open_blocks(table, team_key)
        size = max((block.size() for block in self.all_matching(row_table=table, team_key=team_key)), default=0)
        return not blocks or sum(block.spare_count() for block in blocks) < size + size // RESERVE_SHARE
