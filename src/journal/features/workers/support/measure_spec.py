from collections.abc import Callable
from dataclasses import dataclass

from journal.features.workers.support.measure_range import MeasureRange
from journal.features.workers.support.measure_source import MeasureSource


@dataclass(frozen=True)
class MeasureSpec:
    """One fitness measure of a mode: its key, its range, the reader of its raw value from a measure source, how close a value comes to the range, its weight in the score, the half-life its value is smoothed with, 0 for a value taken as it is, and the words the page names it by."""

    key: str
    range: MeasureRange
    reader: Callable[[MeasureSource], float | None]
    closeness: Callable[[float, MeasureRange], float]
    weight: int
    smoothing_minutes: float = 0.0
    label: str = ""
