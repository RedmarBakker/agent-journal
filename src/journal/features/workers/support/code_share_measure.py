from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts

# the fewest lines landed in the window a share is scored on
LEAST_LINES = 20


@dataclass(frozen=True)
class CodeShareMeasure:
    """The measure of how much of the code landed in the window the builder wrote itself: its own edited lines against the lines merged from its workers, whole at the full-score share and falling straight to nothing at the zero-score share; both and its weight are the user's settings."""

    label: str
    advice: str

    def weighted(self, counts: ToolUseCounts) -> int:
        return counts.code_share.weight

    def closeness(self, counts: ToolUseCounts) -> float | None:
        total = counts.edited_lines + counts.merged_lines
        if total < LEAST_LINES:
            return None
        share, limits = counts.edited_lines / total, counts.code_share
        if share >= limits.full:
            return 1.0
        return max(0.0, (share - limits.zero) / max(limits.full - limits.zero, 0.01))

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        total = max(counts.edited_lines + counts.merged_lines, 1)
        return FitnessGap(self.label, round(100 * counts.edited_lines / total), round(100 * counts.code_share.zero), 100, self.advice)
