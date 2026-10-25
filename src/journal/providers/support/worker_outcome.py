from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerOutcome:
    """What a headless run of a program left: its report, the session it ran in, the error it ended on, empty when it ended well, and what it cost in dollars, 0 when the program does not say."""

    report: str
    session: str = ""
    error: str = ""
    cost_dollars: float = 0.0
