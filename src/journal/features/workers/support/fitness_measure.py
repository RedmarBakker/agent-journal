from dataclasses import dataclass
from typing import Callable

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts


@dataclass(frozen=True)
class FitnessMeasure:
    """One measure of a work mode's ideal agent: the share it reads from the agent's newest tool uses, as a part of a whole, the range an ideal agent of the mode keeps it in, how much it weighs in the score, and what to do when it falls outside."""

    label: str
    share: Callable[[ToolUseCounts], tuple[int, int]]
    low: float
    high: float
    weight: int
    advice: str

    def closeness(self, counts: ToolUseCounts) -> float | None:
        part, total = self.share(counts)
        if not total:
            return None
        value = part / total
        return max(0.0, 1.0 - 2 * self.distance(value))

    def distance(self, value: float) -> float:
        return max(self.low - value, value - self.high, 0.0)

    def percent(self, counts: ToolUseCounts) -> int:
        part, total = self.share(counts)
        return round(100 * part / total) if total else 0

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        return FitnessGap(self.label, self.percent(counts), round(100 * self.low), round(100 * self.high), self.advice)
