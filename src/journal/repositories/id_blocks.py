from journal.models.id_block import IdBlock
from journal.repositories.repository import Repository
from journal.support.actor import Actor
from journal.repositories.number_shortage import NumberShortage

RESERVE_SHARE = 5


class IdBlocks(Repository[IdBlock]):
    """The row numbers this machine holds per table, oldest block first; a used block is removed, and a table wants a new one once fewer numbers are left than a block and a fifth of one."""

    model = IdBlock

    def add(self, table: str, first: int, last: int) -> IdBlock:
        return self.save(IdBlock(row_table=table, first_number=first, last_number=last, next_number=first), Actor.system())

    def next_id(self, table: str) -> int:
        numbers = self.taken(table, 1)
        if not numbers:
            raise NumberShortage(f"every row number this machine holds for {table} is used, and the team server gave no more")
        return numbers[0]

    def taken(self, table: str, count: int) -> list[int]:
        numbers = []
        for block in self.all_matching(row_table=table):
            if len(numbers) == count:
                break
            share = min(count - len(numbers), block.spare_count())
            numbers.extend(range(block.next_number, block.next_number + share))
            if share < block.spare_count():
                self.save(block.past(share), Actor.system())
            else:
                self.delete(block, Actor.system())
        return numbers

    def clear(self) -> None:
        self.purged_rows(IdBlock, self.query(), Actor.system())

    def has_numbers(self, table: str) -> bool:
        return bool(self.all_matching(row_table=table))

    def is_wanted(self, table: str) -> bool:
        blocks = self.all_matching(row_table=table)
        size = max((block.size() for block in blocks), default=0)
        return not blocks or sum(block.spare_count() for block in blocks) < size + size // RESERVE_SHARE
