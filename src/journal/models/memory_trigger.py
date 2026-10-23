from enum import StrEnum


class MemoryTrigger(StrEnum):
    """The moments that bring a fact, rule or reminder to the agent besides its keywords."""

    TASK_COMPLETED = "task_completed"
    TASK_STARTED = "task_started"
