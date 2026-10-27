from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceHealth:
    """What one service's health socket answered in one environment: its service's name, whether a valid answer came within the window, and how long it took."""

    service: str
    answered: bool
    seconds: float
