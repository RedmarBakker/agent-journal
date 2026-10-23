from dataclasses import dataclass


@dataclass(frozen=True)
class AgentViewList:
    """The latest agent view of each environment key asked for that its host sent within the server's freshness limit."""

    views: dict[str, list[dict]]
