from dataclasses import dataclass, field

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class DeliveryRecord(Scoped):
    """One immutable delivery evidence event or its proposed, accepted, corrected or reopened state."""

    state: str = ""
    generation: int = 1
    assurance: str = ""
    policy_version: str = ""
    fingerprint: str = ""
    evidence: dict = field(default_factory=dict)
    reason: str = ""
