from collections import Counter
from contextvars import ContextVar

from journal.models.support.request_loads import RequestLoads

TALLY: ContextVar[Counter | None] = ContextVar("loads", default=None)


class LoadTally:
    """The rows the current request or hook turns into models, by table, while load counting is on: the measurement starts and ends it, and the repository's one load funnel adds each row; outside a started tally a load costs one lookup and counts nothing."""

    @staticmethod
    def begin() -> None:
        TALLY.set(Counter())

    @staticmethod
    def counted(table: str) -> None:
        tally = TALLY.get()
        if tally is not None:
            tally[table] += 1

    @staticmethod
    def ended() -> RequestLoads:
        tally = TALLY.get()
        TALLY.set(None)
        return RequestLoads.tallied(tally) if tally else RequestLoads()
