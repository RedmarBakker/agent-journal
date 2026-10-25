from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.fitness_measure import FitnessMeasure
from journal.features.workers.support.fitness_score import FitnessScore
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
    measures: tuple[FitnessMeasure, ...]

    def scored(self, counts: ToolUseCounts) -> FitnessScore:
        if counts.mode != self.mode or counts.mode_uses < WORK_WINDOW_USES:
            return FitnessScore(self.mode, 100, is_measured=False)
        if counts.file_edits + counts.handovers + counts.subagent_dispatches + counts.research_count < LEAST_ACTIONS:
            return FitnessScore(self.mode, 100, is_measured=False)
        weighed = [(measure, closeness) for measure in self.measures if (closeness := measure.closeness(counts)) is not None]
        if not weighed:
            return FitnessScore(self.mode, 100, is_measured=False)
        score = round(100 * sum(measure.weight * closeness for measure, closeness in weighed) / sum(measure.weight for measure, _ in weighed))
        worst = sorted((pair for pair in weighed if pair[1] < 1.0), key=lambda pair: pair[1] * pair[0].weight - pair[0].weight)
        gaps = tuple(FitnessGap(measure.label, measure.percent(counts), round(100 * measure.low), round(100 * measure.high), measure.advice) for measure, _ in worst[:GAP_COUNT])
        return FitnessScore(self.mode, score, gaps)
