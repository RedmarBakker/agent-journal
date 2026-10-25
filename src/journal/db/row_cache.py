import threading
from collections import OrderedDict
from typing import Callable

STORED_READS_COUNT = 4000


class RowCache:
    """The rows of recent reads, stored by the SQL that read them and the tables it reads, so a read that comes again before any of those tables is written is answered from memory. Each table has a version that every write moves; a read stores its rows only when none of its tables moved while it ran, so a read racing a write never keeps what the write replaced. A read a write is about to change can be stored with the rows the write leaves, at the versions the write's commit leaves. The oldest reads go first past STORED_READS_COUNT."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._versions: dict[str, int] = {}
        self._reads: OrderedDict[tuple, tuple[tuple[int, ...], list]] = OrderedDict()

    def rows(self, tables: tuple[str, ...], key: tuple, reader: Callable[[], list]) -> list:
        with self._lock:
            versions = self.table_versions(tables)
            entry = self._reads.get(key)
            if entry is not None and entry[0] == versions:
                self._reads.move_to_end(key)
                return list(entry[1])
        rows = reader()
        self.stored(tables, key, rows, versions)
        return list(rows)

    def current(self, tables: tuple[str, ...], key: tuple) -> list:
        with self._lock:
            entry = self._reads.get(key)
            return list(entry[1]) if entry is not None and entry[0] == self.table_versions(tables) else []

    def stored(self, tables: tuple[str, ...], key: tuple, rows: list, versions: tuple[int, ...]) -> None:
        with self._lock:
            if versions == self.table_versions(tables):
                self._reads[key] = (versions, rows)
                self._reads.move_to_end(key)
                while len(self._reads) > STORED_READS_COUNT:
                    self._reads.popitem(last=False)

    def table_versions(self, tables: tuple[str, ...]) -> tuple[int, ...]:
        return tuple(self._versions.get(table, 0) for table in tables)

    def changed(self, table: str) -> None:
        with self._lock:
            self._versions[table] = self._versions.get(table, 0) + 1

    def cleared(self) -> None:
        with self._lock:
            self._versions = {table: version + 1 for table, version in self._versions.items()}
            self._reads.clear()
