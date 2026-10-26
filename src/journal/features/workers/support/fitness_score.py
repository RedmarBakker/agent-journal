from dataclasses import dataclass


@dataclass(frozen=True)
class FitnessScore:
    """How close an agent comes to its work mode's measures, from 0 to 100, with how close each measured one came in percent; scored only once the mode has been measured long enough; and the version of the scoring that worked it out."""

    mode: str
    score: int
    is_measured: bool = True
    parts: tuple[tuple[str, int], ...] = ()
    version: int = 1
