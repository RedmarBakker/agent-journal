from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts


@dataclass(frozen=True)
class LoadLevelMeasure:
    """The measure of the level the agent lets its load stand at: whole at or under the full level and falling straight to nothing at the zero level, as its last measure on its row holds it; not counted while its load is unmeasured."""

    label: str
    weight: int
    advice: str
    full_at: float
    zero_at: float

    def closeness(self, counts: ToolUseCounts) -> float | None:
        if not counts.load.is_measured():
            return None
        return max(0.0, min(1.0, (self.zero_at - counts.load.rho) / (self.zero_at - self.full_at)))

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        return FitnessGap(self.label, round(100 * counts.load.rho), 0, round(100 * self.full_at), self.advice)
