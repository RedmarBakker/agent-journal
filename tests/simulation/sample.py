from dataclasses import dataclass

from journal.features.workers.support.tool_use_counts import ToolUseCounts


@dataclass(frozen=True)
class Sample:
    """What the fitness and the load read after one of the agent's actions in a run: the simulated second, the counts its score is worked out from, and its load ρ."""

    second: int
    counts: ToolUseCounts
    rho: float
