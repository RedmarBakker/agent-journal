from dataclasses import dataclass


@dataclass(frozen=True)
class CodeShareLimits:
    """The settings the share of the builder's own code is scored by: the share at full score, the share at no score and how much the measure weighs."""

    full: float = 0.67
    zero: float = 0.33
    weight: int = 4
