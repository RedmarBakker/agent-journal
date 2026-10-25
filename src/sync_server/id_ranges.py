from sync_server.db.id_block_rows import IdBlockRows
from sync_server.db.store import Store
from sync_server.team_details import TeamDetails

# the bits below the team's number T in a row number, so a team's numbers are T * 2^32 + n, apart from every other team's
TEAM_NUMBER_SHIFT = 32


class IdRanges:
    """The blocks of row numbers handed to each device per table, each above every number handed out before, above the highest a journal already had when it became shared, and from T * 2^32 on for a team of number T, so no two machines ever give one number and two teams' numbers never meet."""

    def __init__(self, store: Store, rows: IdBlockRows, details: TeamDetails) -> None:
        self.store, self.rows, self.details = store, rows, details

    def block(self, device_id: int, table: str, size: int) -> tuple[int, int]:
        with self.store.transaction():
            first = max(self.rows.last_number(table), self.rows.floor_number(table), self.details.number() << TEAM_NUMBER_SHIFT) + 1
            self.rows.insert(device_id, table, first, first + size - 1)
            return first, first + size - 1

    def raise_floor(self, table: str, highest: int) -> None:
        self.rows.raise_floor(table, highest)
