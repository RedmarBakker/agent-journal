from enum import StrEnum


class ProfileType(StrEnum):
    """What an agent profile is for: a worker that writes, or a subagent that only reads."""

    WORKER = "worker"
    SUBAGENT = "subagent"
