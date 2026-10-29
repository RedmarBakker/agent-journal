from dataclasses import dataclass


@dataclass(frozen=True)
class TimelineMoment:
    """One task or communication event on a plan's timeline, oldest first."""

    time: float
    moment_type: str
    task: int
    title: str
    text: str = ""
    address: str = ""
    failure: str = ""
