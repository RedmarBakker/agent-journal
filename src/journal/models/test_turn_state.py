from enum import StrEnum


class TestTurnState(StrEnum):
    """Where a worker's turn to run tests stands: waiting for a free run, running, or ended."""

    __test__ = False

    WAITING = "waiting"
    RUNNING = "running"
    ENDED = "ended"
