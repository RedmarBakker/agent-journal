import re
import sqlite3
import threading
import time
import weakref
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import Callable, Iterator

from journal.db.empty_result import EmptyResult
from journal.db.relation_read import RelationRead
from journal.db.row_cache import RowCache
from journal.support.masks import Masks
from journal.support.large_reads import LargeReads
from journal.support.query_times import QueryTimes
from journal.support.stage_times import StageTimes

# the table a read takes its rows from, the first one the query builder's text names
READ_TABLE = re.compile(r"^SELECT\b.*?\bFROM\s+(\w+)", re.DOTALL)


class Connection:
    """The one place SQL is executed, a secret value masked out of every text it writes. Each thread reads on a sqlite connection leased from a pool, returned with release() or, by any thread that never says so, once the thread is gone, so no thread that ends leaves one open; writes take the one lock, so the threaded server never contends. Reads of rows may be answered from the row cache, which every write and every commit of a table moves on, and a rolled-back transaction clears. While a thread lists one table, a read of another table's rows raises, save one made unlisted: a count, or the environment a request names."""

    def __init__(self, path: Path, masks: Masks, stages: StageTimes, queries: QueryTimes, large_reads: LargeReads) -> None:
        self.path, self.masks, self.stages, self.queries, self.large_reads = path, masks, stages, queries, large_reads
        self._threads = threading.local()
        self._writing = threading.RLock()
        self._pooling = threading.Lock()
        self._open: list[sqlite3.Connection] = []
        self._free: list[sqlite3.Connection] = []
        self.cache = RowCache()

    def release(self) -> None:
        local = getattr(self._threads, "connection", None)
        if local is None:
            return
        self._threads.connection = None
        self._threads.returned.detach()
        self._returned(local)

    def _returned(self, local: sqlite3.Connection) -> None:
        with self._pooling:
            self._free.append(local)

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.timed(sql, params, lambda cursor: cursor)

    def one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        return self.timed(sql, params, lambda cursor: cursor.fetchone())

    def result(self, sql: str, params: tuple = ()) -> sqlite3.Row:
        row = self.one(sql, params)
        if row is None:
            raise EmptyResult(sql)
        return row

    def all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.timed(sql, params, lambda cursor: cursor.fetchall())

    def timed(self, sql: str, params: tuple, cursor_reader: Callable[[sqlite3.Cursor], object]):
        self._guarded(sql)
        began = time.perf_counter()
        try:
            return cursor_reader(self._local().execute(sql, self.masks.masked(params)))
        finally:
            self.queries.add(sql, params, time.perf_counter() - began)

    def execute_many(self, sql: str, rows: list[tuple]) -> None:
        began = time.perf_counter()
        try:
            self._local().executemany(sql, [self.masks.masked(params) for params in rows])
        finally:
            self.queries.add(sql, rows[0] if rows else (), time.perf_counter() - began)

    def plan(self, sql: str, params: tuple) -> list[str]:
        return [row["detail"] for row in self._local().execute(f"EXPLAIN QUERY PLAN {sql}", self.masks.masked(params)).fetchall()]

    def cached(self, tables: tuple[str, ...], sql: str, params: tuple, reader: Callable[[list[sqlite3.Row]], list]) -> list:
        self._guarded(sql)
        if self.is_thread_writing(tables):
            return self.loaded_rows(tables[0], sql, params, reader)
        return self.cache.rows(tables, (sql, params), lambda: self.loaded_rows(tables[0], sql, params, reader))

    def stored_rows(self, tables: tuple[str, ...], sql: str, params: tuple) -> list:
        """The rows the cache holds for a read, current and as this thread would see them; none when it holds none or this thread has written its tables in its open transaction."""
        if not self._local().in_transaction or self.is_thread_writing(tables):
            return []
        return self.cache.current(tables, (sql, params))

    def holds_secret(self, params: tuple) -> bool:
        """Whether a write of these values would be masked, so what it stores differs from them."""
        return self.masks.holds_secret(params)

    def rewritten(self, tables: tuple[str, ...], sql: str, params: tuple, rows: list) -> None:
        """A read the open transaction's write has just changed, answered with rows once the transaction commits, unless another write moves its tables first."""
        self._threads.rewritten.append((tables, (sql, params), rows, self.cache.table_versions(tables)))

    def is_thread_writing(self, tables: tuple[str, ...]) -> bool:
        return self._local().in_transaction and bool(set(tables) & getattr(self._threads, "written", set()))

    def loaded_rows(self, table: str, sql: str, params: tuple, reader: Callable[[list[sqlite3.Row]], list]) -> list:
        with self.stages.timed(f"read {table}"):
            return reader(self.all(sql, params))

    @contextmanager
    def listing(self, table: str) -> Iterator[None]:
        listed = getattr(self._threads, "listed", "")
        self._threads.listed = table
        try:
            yield
        finally:
            self._threads.listed = listed

    def unlisted(self) -> AbstractContextManager[None]:
        return self.listing("")

    def _guarded(self, sql: str) -> None:
        listed = getattr(self._threads, "listed", "")
        read = READ_TABLE.match(sql) if listed else None
        if read and read.group(1) != listed:
            raise RelationRead(listed, read.group(1))

    def changed(self, table: str) -> None:
        self.cache.changed(table)
        if self._local().in_transaction:
            self._threads.written.add(table)

    @contextmanager
    def transaction(self) -> Iterator["Connection"]:
        local = self._local()
        if local.in_transaction:
            with self._writing:
                yield self
            return
        with self.stages.timed("write lock wait"):
            self._writing.acquire()
        try:
            local.execute("BEGIN IMMEDIATE")
            self._threads.committed, self._threads.written, self._threads.rewritten = [], set(), []
            try:
                with self.stages.timed("write"):
                    yield self
            except BaseException:
                local.execute("ROLLBACK")
                self._threads.committed, self._threads.rewritten = [], []
                self.cache.cleared()
                raise
            local.execute("COMMIT")
            written = self._threads.__dict__.pop("written", set())
            for table in written:
                self.cache.changed(table)
            for tables, key, rows, versions in self._threads.__dict__.pop("rewritten", []):
                self.cache.stored(tables, key, rows, tuple(version + (table in written) for table, version in zip(tables, versions)))
        finally:
            self._writing.release()
        for work in self._threads.__dict__.pop("committed", []):
            work()

    def commit_callback(self, work: Callable[[], None]) -> None:
        if self._local().in_transaction:
            self._threads.committed.append(work)
            return
        work()

    def backup(self, target: Path) -> None:
        copy = sqlite3.connect(target)
        self._local().backup(copy)
        copy.close()

    def close(self) -> None:
        for open_ in self._open:
            open_.close()
        self._open.clear()

    def _local(self) -> sqlite3.Connection:
        local = getattr(self._threads, "connection", None)
        if local is None:
            local = self._leased()
            self._threads.connection = local
            self._threads.returned = weakref.finalize(threading.current_thread(), self._returned, local)
        return local

    def _leased(self) -> sqlite3.Connection:
        with self._pooling:
            if self._free:
                return self._free.pop()
            local = sqlite3.connect(self.path, autocommit=True, check_same_thread=False)
            local.row_factory = sqlite3.Row
            local.execute("PRAGMA journal_mode=WAL")
            local.execute("PRAGMA synchronous=NORMAL")
            local.execute("PRAGMA foreign_keys=ON")
            local.execute("PRAGMA busy_timeout=5000")
            self._open.append(local)
            return local
