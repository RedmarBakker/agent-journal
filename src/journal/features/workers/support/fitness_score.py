from dataclasses import dataclass

from journal.features.workers.support.fitness_gap import FitnessGap


@dataclass(frozen=True)
class FitnessScore:
    """How close an agent's newest tool uses come to its work mode's ideal, from 0 to 100, with the measures furthest off it, worst first; scored only once the agent has done enough to be measured; less the points still unrecovered of a quick report's drop, with what caused it."""

    mode: str
    score: int
    gaps: tuple[FitnessGap, ...] = ()
    is_measured: bool = True
    parts: tuple[tuple[str, int], ...] = ()
    drop_points: int = 0
    drop_cause: str = ""

    @property
    def lines(self) -> tuple[str, ...]:
        return tuple(gap.text() for gap in self.gaps)
