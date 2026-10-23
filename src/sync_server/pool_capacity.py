from dataclasses import dataclass
from sqlite3 import Row


@dataclass(frozen=True)
class PoolCapacity:
    """The worker slots a machine gives the team's pool as its last pull named them: its device, the slots, how many are free, the journal version it runs and when it sent so."""

    device_id: int
    slots: int
    free: int
    version: str
    reported_at: float

    @classmethod
    def stored(cls, row: Row) -> "PoolCapacity":
        return cls(row["device_id"], row["slots"], row["free"], row["version"], row["reported_at"])
