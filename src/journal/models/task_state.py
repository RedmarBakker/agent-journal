from enum import StrEnum


# a state's name before it was renamed, which a row kept elsewhere, as the team's copy, may still carry
FORMER_NAMES = {"parked": "paused"}


class TaskState(StrEnum):
    OPEN = "open"
    STARTED = "started"
    DELEGATED = "delegated"
    PAUSED = "paused"
    BLOCKED = "blocked"
    FINISHED = "done"
    CANCELLED = "cancelled"

    @classmethod
    def _missing_(cls, value: object) -> "TaskState | None":
        return cls(FORMER_NAMES[value]) if value in FORMER_NAMES else None

    def is_closed(self) -> bool:
        return self in (TaskState.FINISHED, TaskState.CANCELLED)
