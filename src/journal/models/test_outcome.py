from enum import StrEnum


class TestOutcome(StrEnum):
    """How a worker's test run came out: passed, failed, or not known, as for one still going or stopped before it ended."""

    __test__ = False

    UNKNOWN = ""
    PASSED = "passed"
    FAILED = "failed"
