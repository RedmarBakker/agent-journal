import time

from journal.support.timeout import Timeout

WAIT_SECONDS = 30
TOLERANCE_SECONDS = 2


def waited(began: float) -> bool:
    # @sin SpanWorkedOutByHandDetector
    # @sin HandWrittenIntervalDetector
    return time.monotonic() - began >= WAIT_SECONDS


def overdue(started_at: float, moment: float) -> bool:
    # @sin SpanWorkedOutByHandDetector
    # @sin HandWrittenIntervalDetector
    return moment - started_at > WAIT_SECONDS


def recent_count(stamps: list[float], moment: float) -> int:
    # @sin SpanWorkedOutByHandDetector
    return sum(1 for stamp in stamps if moment - WAIT_SECONDS < stamp <= moment)


def waited_plainly(began: float) -> bool:
    # @fixed SpanWorkedOutByHandDetector
    return Timeout.seconds(WAIT_SECONDS).started(began).is_elapsed(time.monotonic())


def drift(offset: float, expected: float) -> bool:
    # @righteous SpanWorkedOutByHandDetector
    return abs(offset - expected) > TOLERANCE_SECONDS
