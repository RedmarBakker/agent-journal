from dataclasses import dataclass


@dataclass(frozen=True)
class JobSpan:
    """The span of a worker's job, from the move that started it to its merge, and the send-backs in it."""

    start: float
    end: float
    rejection_count: int
