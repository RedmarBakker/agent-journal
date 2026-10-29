from datetime import datetime


class SessionTakeovers:
    """The last-seen time of an agent session replaced as a new session starts, kept until that start's briefing reads it."""

    def __init__(self) -> None:
        self._last_seen: dict[tuple[int, str], datetime] = {}

    def remember(self, environment_id: int, session: str, last_seen: datetime) -> None:
        self._last_seen[(environment_id, session)] = last_seen

    def take(self, environment_id: int, session: str) -> datetime | None:
        return self._last_seen.pop((environment_id, session), None)
