from enum import StrEnum


class PressureBand(StrEnum):
    """Where the worker queue stands for a mode with workers: low, normal or high; solo has no band."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    NONE = "none"
