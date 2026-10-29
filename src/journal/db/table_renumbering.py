from journal.db.connection import Connection
from journal.models.link import Link


class TableRenumbering:
    """The SQL that gives rows of the shared tables new numbers in one transaction: each table's ids moved, the columns that name a moved row rewritten, the link ends renamed, the person stamps changed and the tables named cleared."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def ids(self, storage: str) -> list[int]:
        return [row["id"] for row in self.connection.all(f"SELECT id FROM {storage} ORDER BY id")]

    def renumbered(self, moves: dict[str, dict[int, int]], remaps: list[tuple[str, str, dict[int, int]]], refs: dict[str, dict[int, int]], restamps: list[tuple[str, str, str, str]], cleared: tuple[str, ...]) -> None:
        with self.connection.transaction() as db:
            for storage, numbers in moves.items():
                self.moved_ids(db, storage, numbers)
            for storage, column, numbers in remaps:
                self.remapped(db, storage, column, numbers)
            self.linked(db, refs)
            for storage, column, old_stamp, new_stamp in restamps:
                db.execute(f"UPDATE {storage} SET {column} = ? WHERE {column} = ?", (new_stamp, old_stamp))
            for storage in cleared:
                db.execute(f"DELETE FROM {storage}")
        self.connection.cache.cleared()

    @staticmethod
    def moved_ids(db, storage: str, numbers: dict[int, int]) -> None:
        db.execute_many(f"UPDATE {storage} SET id = ? WHERE id = ?", [(-new, old) for old, new in numbers.items()])
        db.execute(f"UPDATE {storage} SET id = -id WHERE id < 0")

    @staticmethod
    def remapped(db, storage: str, column: str, numbers: dict[int, int]) -> None:
        rows = db.all(f"SELECT id, {column} AS value FROM {storage}")
        db.execute_many(f"UPDATE {storage} SET {column} = ? WHERE id = ?", [(numbers[row["value"]], row["id"]) for row in rows if row["value"] in numbers])

    @staticmethod
    def linked(db, refs: dict[str, dict[int, int]]) -> None:
        rows = db.all(f"SELECT id, source, target FROM {Link.storage()}")
        db.execute_many(f"UPDATE {Link.storage()} SET source = ?, target = ? WHERE id = ?", [(TableRenumbering.moved_ref(row["source"], refs), TableRenumbering.moved_ref(row["target"], refs), row["id"]) for row in rows])

    @staticmethod
    def moved_ref(ref: str, refs: dict[str, dict[int, int]]) -> str:
        table, _, number = ref.rpartition(":")
        return f"{table}:{refs[table][int(number)]}" if number.isdigit() and int(number) in refs.get(table, {}) else ref
