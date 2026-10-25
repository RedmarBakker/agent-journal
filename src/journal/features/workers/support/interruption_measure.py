from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts


@dataclass(frozen=True)
class InterruptionMeasure:
    """The measure of how often workers interrupt their dispatcher: the reports an hour they filed over the window while plenty of work was open, whole up to the full-score rate and falling straight to nothing at the zero-score rate; a report with little else open costs nothing, and no report at all leaves it unmeasured."""

    label: str
    weight: int
    advice: str

    def closeness(self, counts: ToolUseCounts) -> float | None:
        use = counts.report_use
        if not use.is_measured:
            return None
        if use.hourly_reports <= use.full_hourly_reports:
            return 1.0
        return max(0.0, (use.zero_hourly_reports - use.hourly_reports) / max(use.zero_hourly_reports - use.full_hourly_reports, 1.0))

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        use = counts.report_use
        return FitnessGap(self.label, round(use.hourly_reports, 1), 0, round(use.full_hourly_reports, 1), self.advice, " an hour")
