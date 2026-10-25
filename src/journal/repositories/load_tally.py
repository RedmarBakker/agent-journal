import threading
from contextvars import ContextVar

from journal.models.support.request_loads import RequestLoads
from journal.repositories.load_counters import LoadCounters


TALLY: ContextVar[LoadCounters | None] = ContextVar("loads", default=None)


class LoadTally:
    """The rows the current request or hook turns into models, with their bytes, and the writes it makes, by table, while load counting is on: the measurement starts and ends it, one started inside another counting into the outer one, and the repository's load and write funnels add to it on the thread that started it alone, so work deferred past the reply, which carries the request's context, never counts against it; outside a started tally each costs one lookup and counts nothing."""

    @staticmethod
    def begin() -> None:
        tally = LoadTally.running()
        if tally is None:
            TALLY.set(LoadCounters())
            return
        tally.depth += 1

    @staticmethod
    def counted(table: str, row) -> None:
        tally = LoadTally.running()
        if tally is not None:
            tally.rows[table] += 1
            tally.sizes[table] += sum(len(value) if isinstance(value, (str, bytes)) else 8 for value in row)

    @staticmethod
    def count_write(table: str) -> None:
        tally = LoadTally.running()
        if tally is not None:
            tally.writes[table] += 1

    @staticmethod
    def running() -> LoadCounters | None:
        tally = TALLY.get()
        return tally if tally is not None and tally.thread == threading.get_ident() else None

    @staticmethod
    def ended() -> RequestLoads:
        tally = TALLY.get()
        if tally is None:
            return RequestLoads()
        tally.depth -= 1
        if tally.depth == 0:
            TALLY.set(None)
        return RequestLoads.measured(tally.rows, tally.sizes, tally.writes)
