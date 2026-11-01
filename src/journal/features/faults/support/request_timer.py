import time
from dataclasses import dataclass


@dataclass
class RequestTimer:
    """A request's start time and the one-time end of the load tally it opened."""

    request_at: float
    loads_started: bool = False
    loads_ended: bool = False

    def wall_ms(self) -> float:
        return (time.time() - self.request_at) * 1000
