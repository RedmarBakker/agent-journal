from dataclasses import dataclass


@dataclass(frozen=True)
class QueueWalk:
    """A queue walked minute by minute: each minute's time, smoothed ρ and weight waiting, and the smoothed arrivals, clearings and wait at its end, the clearings and the wait None where none was measured."""

    points: tuple[tuple[float, float, float], ...]
    arrivals: float
    clearings: float | None
    wait_minutes: float | None
