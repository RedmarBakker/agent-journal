from dataclasses import dataclass


@dataclass(frozen=True)
class HalfLife:
    """Exponential smoothing by a half-life in minutes: a step moves the smoothed value toward the new one by the share its seconds give."""

    minutes: float

    def share(self, seconds: float) -> float:
        return 1 - 0.5 ** (seconds / (self.minutes * 60))

    def folded(self, smoothed: float, value: float, seconds: float) -> float:
        return smoothed + self.share(seconds) * (value - smoothed)
