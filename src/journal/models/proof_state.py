from enum import StrEnum


class ProofState(StrEnum):
    """The state of a proof of one point of a worker's brief: shown by the worker, or not done with the reason, then checked or sent back as short, or stale once the point's wording changed."""

    SHOWN = "shown"
    UNFINISHED = "not done"
    CHECKED = "checked"
    CHECKED_UNFINISHED = "checked, not done"
    SHORT = "short"
    STALE = "stale"
