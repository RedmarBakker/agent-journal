from dataclasses import dataclass


@dataclass(frozen=True)
class PoolSlots:
    """How many workers a machine offers the team's pool, and how many of them are free now."""

    slots: int
    free: int
