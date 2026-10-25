from enum import StrEnum


# a state's name before it was renamed, which a row kept elsewhere, as the team's copy, may still carry
FORMER_NAMES = {"parked": "paused", "done": "completed", "delegated": "started"}


class TaskState(StrEnum):
    OPEN = "open"
    STARTED = "started"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def _missing_(cls, value: object) -> "TaskState | None":
        return cls(FORMER_NAMES[value]) if value in FORMER_NAMES else None

    def is_closed(self) -> bool:
        return self in (TaskState.COMPLETED, TaskState.CANCELLED)
