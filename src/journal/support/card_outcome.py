from enum import StrEnum


class CardOutcome(StrEnum):
    """How the thing a card stands for stands, which the viewer colours: running blue, passed green, failed red and warned orange; a plain event has none."""

    NONE = ""
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNED = "warned"
