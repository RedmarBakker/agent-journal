import time


class Stamp:
    """A sample for wall-clock-outside-time-source: a moment read from the wall clock, and one read from the time source."""

    def __init__(self, time_source) -> None:
        self.time_source = time_source

    def clock_time(self) -> float:
        # @sin WallClockOutsideTimeSourceDetector
        return time.time()

    def current(self) -> float:
        return self.time_source.seconds()
