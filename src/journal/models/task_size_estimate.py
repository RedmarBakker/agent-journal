from dataclasses import dataclass

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class TaskSizeEstimate(Scoped):
    """One immutable planning size, revision, first-ready snapshot or worker proposal."""

    change_type: str = ""
    size: int | None = None
    reason: str = ""
    scale_version: str = ""
