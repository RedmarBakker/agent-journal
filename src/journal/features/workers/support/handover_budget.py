from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class HandoverBudget:
    """The lines the builder wrote itself since its last handover against the lines one worker out is worth, which the mode panel warns of while the first are fewer."""

    lines: int
    budget: int

    def as_data(self) -> dict:
        return asdict(self)
