import time

from journal.support.timeout import Timeout

WAIT_SECONDS = 30
TOLERANCE_SECONDS = 2


def waited(began: float) -> bool:
    # @sin SpanWorkedOutByHandDetector
    return time.monotonic() - began >= WAIT_SECONDS


def overdue(started_at: float, moment: float) -> bool:
    # @sin SpanWorkedOutByHandDetector
    return moment - started_at > WAIT_SECONDS


def recent(times: list[float], moment: float) -> int:
    # @sin SpanWorkedOutByHandDetector
    return sum(1 for seen in times if moment - WAIT_SECONDS < seen <= moment)


def waited_plainly(began: float) -> bool:
    # @fixed SpanWorkedOutByHandDetector
    return Timeout.seconds(WAIT_SECONDS).started(began).is_elapsed(time.monotonic())


def drifted(offset: float, seconds: float) -> bool:
    # @righteous SpanWorkedOutByHandDetector
    return abs(offset - seconds) > TOLERANCE_SECONDS
