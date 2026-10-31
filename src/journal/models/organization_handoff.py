from dataclasses import dataclass
from datetime import datetime

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class OrganizationHandoff(Scoped):
    """A task waiting in one generated organization seat's journal inbox."""

    target: str = ""
    read_at: datetime | None = None

    def read(self, at: datetime) -> "OrganizationHandoff":
        return self.with_(read_at=at)

    def unread(self) -> "OrganizationHandoff":
        return self.with_(read_at=None)
