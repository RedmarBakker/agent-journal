from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts

# the fewest lines landed in the window a share is scored on
LEAST_LINES = 20


@dataclass(frozen=True)
class OwnShareMeasure:
    """The measure of how much of the code landed in the window the builder wrote itself: its own edited lines against the lines merged from its workers, whole at the full-score share and falling straight to nothing at the zero-score share; both and its weight are the user's settings."""

    label: str
    advice: str

    def weight_of(self, counts: ToolUseCounts) -> int:
        return counts.own_share.weight

    def closeness(self, counts: ToolUseCounts) -> float | None:
        total = counts.own_lines + counts.landed_lines
        if total < LEAST_LINES:
            return None
        share, limits = counts.own_lines / total, counts.own_share
        if share >= limits.full:
            return 1.0
        return max(0.0, (share - limits.zero) / max(limits.full - limits.zero, 0.01))

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        total = max(counts.own_lines + counts.landed_lines, 1)
        return FitnessGap(self.label, round(100 * counts.own_lines / total), round(100 * counts.own_share.zero), 100, self.advice)
