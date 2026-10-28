from dataclasses import dataclass, replace
from typing import ClassVar

from journal.models.model import Model


@dataclass(frozen=True)
class StateTransition(Model):
    """One kind of change of an agent's stack, the state on top before, the state on top after and the event that caused it, with how many times it happened and when it was first and last seen; kept apart from the record, which trims its entries."""

    shared: ClassVar[bool] = False

    before_state: str = ""
    after_state: str = ""
    cause: str = ""
    count: int = 0
    first_at: float = 0.0
    last_at: float = 0.0

    def happened(self, at: float) -> "StateTransition":
        return replace(self, count=self.count + 1, first_at=self.first_at or at, last_at=at)

    def kind(self) -> str:
        return f"{self.before_state or 'no state'} > {self.after_state} on {self.cause}"
