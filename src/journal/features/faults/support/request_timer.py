import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestTimer:
    """When a request was sent, by the sender's own stamp or its arrival when it carries none, on the wall clock, so its time counts every wait from that moment to its answer."""

    request_at: float

    def wall_ms(self) -> float:
        return (time.time() - self.request_at) * 1000
