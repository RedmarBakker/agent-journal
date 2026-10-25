from dataclasses import dataclass


@dataclass(frozen=True)
class DepartureAnswer:
    """What the team server withdrew when a person left: how many of their shared environments' rows."""

    withdrawn: int
