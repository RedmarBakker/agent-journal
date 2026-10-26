from dataclasses import dataclass

from journal.models.support.measure_states import MeasureStates
from journal.models.support.pressure_band import PressureBand


@dataclass(frozen=True)
class Sample:
    """What the fitness and the load read after one of the agent's actions in a run: the simulated second, its work load ρ, the state of each measure of its mode and its pressure band."""

    second: int
    rho: float
    measures: MeasureStates
    band: PressureBand
