from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap
from journal.features.workers.support.tool_use_counts import ToolUseCounts

EMPTY_ADVICE = "queue more: give each worker with an empty queue its next tasks with journal worker queue <n> <task>..."
PILING_ADVICE = "let a queue drain: give the next tasks to an idle worker or a worker with a short queue, not to the one piling up"


@dataclass(frozen=True)
class QueueMeasure:
    """The measure of how the orchestrator keeps its workers' queues full and draining: the share of its workers with a history of merges whose queue neither stood empty while tasks were open nor held more than they drain; unmeasured with no such worker, and its advice names the remedy the most workers need."""

    label: str
    weight: int

    def closeness(self, counts: ToolUseCounts) -> float | None:
        use = counts.queue_use
        return use.steady_share() if use.is_measured() else None

    def gap(self, counts: ToolUseCounts) -> FitnessGap:
        use = counts.queue_use
        return FitnessGap(self.label, round(100 * use.steady_share()), 100, 100, EMPTY_ADVICE if use.empty >= use.piling else PILING_ADVICE)
