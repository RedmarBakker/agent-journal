from dataclasses import dataclass, field

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class SprintChange(Scoped):
    """An actor-stamped change to a sprint's scope after its commitment was frozen."""

    change_type: str = ""
    reason: str = ""
    data: dict = field(default_factory=dict)
