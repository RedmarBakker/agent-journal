import threading
from dataclasses import dataclass

READ_CAPACITY = 200


@dataclass(frozen=True)
class LargeRead:
    """A read of more rows than a page, by where it was asked: the table, the query, the file and line of the code that asked, how many times, and the most rows it read or asked for."""

    table: str
    sql: str
    caller: str
    count: int
    largest_rows: int

    def line(self) -> str:
        return f"{self.largest_rows:>7} rows  {self.count:>5} times  {self.table:<18} {self.caller}  {' '.join(self.sql.split())[:160]}"


class LargeReads:
    """Every read of more rows than a page since the last reset, kept in memory for journal developer reads: a page read asking more, which was cut to a page, and a whole-table read that returned more."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.reads: dict[tuple[str, str], LargeRead] = {}

    def add(self, table: str, sql: str, caller: str, rows: int) -> None:
        with self.lock:
            read = self.reads.get((sql, caller))
            if read is None and len(self.reads) >= READ_CAPACITY:
                return
            if read is None:
                read = LargeRead(table, sql, caller, 0, 0)
            self.reads[(sql, caller)] = LargeRead(table, sql, caller, read.count + 1, max(read.largest_rows, rows))

    def largest(self, count: int) -> list[LargeRead]:
        with self.lock:
            return sorted(self.reads.values(), key=lambda read: read.largest_rows, reverse=True)[:count]

    def clear(self) -> None:
        with self.lock:
            self.reads = {}
