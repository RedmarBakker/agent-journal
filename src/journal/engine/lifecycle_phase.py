from enum import Enum


class LifecyclePhase(Enum):
    """Where the journal's server is in its life: loading, or answering."""

    BOOTING = "booting"
    BOOTED = "booted"
