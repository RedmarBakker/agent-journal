from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateData:
    """What the viewer shows of the updates: the version installed, the newer releases out, an update under way and the step it is on, or the last one's problem, and when this journal process started, so a reinstall of the same version is seen to have restarted it."""

    installed: str
    latest: str
    newer: bool
    branch: str
    versions: list[str]
    updating: str
    step: str
    problem: str
    started_at: float
