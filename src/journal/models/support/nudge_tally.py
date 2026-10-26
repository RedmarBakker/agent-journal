from dataclasses import dataclass


@dataclass(frozen=True)
class NudgeTally:
    """How often one nudge reached one agent since the counts were last reset, and when it last did, in seconds."""

    session: str
    key: str
    count: int
    last_at: float
