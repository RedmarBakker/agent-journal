from dataclasses import dataclass, field

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class SprintCommitment(Scoped):
    """A plan's immutable scope snapshot taken when its sprint starts."""

    snapshot: dict = field(default_factory=dict)
