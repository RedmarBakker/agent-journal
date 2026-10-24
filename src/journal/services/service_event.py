from dataclasses import dataclass, field

CHANGE_QUEUED = "change_queued"
TEAM_JOINED = "team_joined"
TEAM_DEPARTURE = "team_departure"
UPGRADE_PREPARING = "upgrade_preparing"
UPGRADE_ABANDONED = "upgrade_abandoned"


@dataclass(frozen=True)
class ServiceEvent:
    """A moment the journal posts to every service registered for it: its name and what the service needs to know of it."""

    name: str
    data: dict = field(default_factory=dict)

    def body(self) -> dict:
        return {"event": self.name, **self.data}
