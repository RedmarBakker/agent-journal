from dataclasses import dataclass


@dataclass(frozen=True)
class TimelineMoment:
    """One event on a plan's task: when, in seconds, what (started, log, ended or done), the task and what was written."""

    time: float
    kind: str
    task: int
    title: str
    text: str = ""
