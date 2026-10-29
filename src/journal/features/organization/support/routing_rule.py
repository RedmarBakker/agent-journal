from dataclasses import dataclass


@dataclass(frozen=True)
class RoutingRule:
    """Advice a Domain agent reads: for this kind of job the primary Role, and the Roles that follow for a real handoff."""

    when: str
    role: str
    then: tuple[str, ...]
