from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts


@dataclass(frozen=True)
class LoadMeasure:
    """The measure of the orchestrator's handling of its load that is a time, not a share: the minutes its load has stayed over the add-a-place level, whole up to the full-score minutes and falling straight to nothing at the zero-score minutes, as its last measure on its row holds them; not counted while its load is unmeasured."""

    label: str
    weight: int
    advice: str

    def closeness(self, counts: ToolUseCounts) -> float | None:
        load = counts.load
        if not load.is_measured():
            return None
        if load.over_minutes <= load.over_full_minutes:
            return 1.0
        return max(0.0, (load.over_zero_minutes - load.over_minutes) / max(load.over_zero_minutes - load.over_full_minutes, 1.0))

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        return FitnessGap(self.label, round(counts.load.over_minutes), 0, round(counts.load.over_full_minutes), self.advice, " minutes")
