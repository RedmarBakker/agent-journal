from dataclasses import dataclass

from journal.models.scoped import Scoped
from journal.models.sprint_state import SprintState


@dataclass(frozen=True)
class Sprint(Scoped):
    """A fixed-length local calendar interval whose UTC boundaries and start commitment freeze when it starts."""

    starts_on: str = ""
    ends_on: str = ""
    starts_at: float = 0.0
    ends_at: float = 0.0
    timezone: str = ""
    length_days: int = 14
    calendar_version: int = 1
    state: SprintState = SprintState.DRAFT
    started_at: float = 0.0
    closed_at: float = 0.0

    def includes(self, moment: float) -> bool:
        return self.starts_at <= moment < self.ends_at

    def activated(self, moment: float) -> "Sprint":
        return self.with_(state=SprintState.ACTIVE, started_at=moment)

    def closed(self, moment: float) -> "Sprint":
        return self.with_(state=SprintState.CLOSED, closed_at=moment)
