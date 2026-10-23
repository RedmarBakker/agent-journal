from dataclasses import dataclass


@dataclass(frozen=True)
class AgentViewPost:
    """The agent views a host sends: for each environment key it hosts, the rows its agent bar shows, empty for an environment with no live agent."""

    views: dict[str, list[dict]]
