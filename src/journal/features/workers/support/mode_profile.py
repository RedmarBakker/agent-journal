from dataclasses import dataclass

from journal.features.workers.support.fitness_measure import FitnessMeasure
from journal.features.workers.support.interruption_measure import InterruptionMeasure
from journal.features.workers.support.load_measure import LoadMeasure
from journal.features.workers.support.queue_measure import QueueMeasure
from journal.features.workers.support.fitness_score import FitnessScore
from journal.features.workers.support.code_share_measure import CodeShareMeasure
from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.models.agent import WORK_WINDOW_USES

# the actions among the newest tool uses, edits, handovers, dispatches and research, an agent shows before it is scored at all
LEAST_ACTIONS = 8
# the measures furthest off the ideal that a low score names
GAP_COUNT = 2


@dataclass(frozen=True)
class ModeProfile:
    """A work mode's ideal agent written down as measures, and an agent's newest tool uses scored against it, once it has made as many in this mode as the score counts over: each measure inside its range counts whole, one outside counts less the further off it is, weighted, so a new mode is a new profile and nothing else."""

    mode: str
    measures: tuple[FitnessMeasure | LoadMeasure | InterruptionMeasure | QueueMeasure | CodeShareMeasure, ...]

    @staticmethod
    def weight(measure: object, counts: ToolUseCounts) -> int:
        return measure.weighted(counts) if isinstance(measure, CodeShareMeasure) else measure.weight

    def scored(self, counts: ToolUseCounts) -> FitnessScore:
        if counts.mode != self.mode or counts.mode_uses < WORK_WINDOW_USES:
            return FitnessScore(self.mode, 100, is_measured=False)
        if counts.file_edits + counts.handovers + counts.subagent_dispatches + counts.research_count < LEAST_ACTIONS:
            return FitnessScore(self.mode, 100, is_measured=False)
        weighed = [(measure, closeness) for measure in self.measures if (closeness := measure.closeness(counts)) is not None]
        if not weighed:
            return FitnessScore(self.mode, 100, is_measured=False)
        score = max(0, round(100 * sum(self.weight(measure, counts) * closeness for measure, closeness in weighed) / sum(self.weight(measure, counts) for measure, _ in weighed)) - counts.report_use.unrecovered_points)
        worst = sorted((pair for pair in weighed if pair[1] < 1.0), key=lambda pair: pair[1] * self.weight(pair[0], counts) - self.weight(pair[0], counts))
        gaps = tuple(measure.gap(counts) for measure, _ in worst[:GAP_COUNT])
        return FitnessScore(self.mode, score, gaps, parts=tuple((measure.label, round(100 * closeness)) for measure, closeness in weighed), drop_points=counts.report_use.unrecovered_points, drop_cause=counts.report_use.drop_cause)
