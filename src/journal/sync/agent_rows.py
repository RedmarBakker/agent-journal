from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRows:
    """An environment's agent bar rows as last read from the team server, and when."""

    rows: list[dict]
    updated_at: float
