import time
from datetime import datetime, timezone


class TimeSource:
    """The journal's one reading of the time: the wall clock, unless a run pins it to a moment of its own, as a simulation does; read to the microsecond, so its seconds and its moment are always the same time."""

    def __init__(self) -> None:
        self.pinned_seconds: float | None = None

    def seconds(self) -> float:
        return self.microsecond_seconds(time.time()) if self.pinned_seconds is None else self.pinned_seconds

    def moment(self) -> datetime:
        return datetime.fromtimestamp(self.seconds(), timezone.utc)

    def pin(self, seconds: float) -> None:
        self.pinned_seconds = self.microsecond_seconds(seconds)

    @staticmethod
    def microsecond_seconds(seconds: float) -> float:
        return datetime.fromtimestamp(seconds, timezone.utc).timestamp()

    def unpin(self) -> None:
        self.pinned_seconds = None
