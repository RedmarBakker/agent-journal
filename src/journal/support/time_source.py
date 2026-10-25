import time
from datetime import datetime, timezone


class TimeSource:
    """The journal's one reading of the time: the wall clock, unless a run pins it to a moment of its own, as a simulation does."""

    def __init__(self) -> None:
        self.pinned_seconds: float | None = None

    def seconds(self) -> float:
        return time.time() if self.pinned_seconds is None else self.pinned_seconds

    def moment(self) -> datetime:
        return datetime.fromtimestamp(self.seconds(), timezone.utc)

    def pin(self, seconds: float) -> None:
        self.pinned_seconds = seconds

    def unpin(self) -> None:
        self.pinned_seconds = None
