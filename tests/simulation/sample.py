from dataclasses import dataclass

from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.models.support.measure_states import MeasureStates


@dataclass(frozen=True)
class Sample:
    """What the fitness and the load read after one of the agent's actions in a run: the simulated second, the counts its score is worked out from, its load ρ and the state of each measure of its mode."""

    second: int
    counts: ToolUseCounts
    rho: float
    measures: MeasureStates
