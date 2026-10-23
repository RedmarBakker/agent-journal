from dataclasses import dataclass


@dataclass(frozen=True)
class AgentView:
    """One environment's agent bar rows as its host last sent them, and when."""

    rows: list[dict]
    updated_at: float
