from collections.abc import Mapping

from journal.engine.support.settings import Settings
from journal.features.tasks.support.wait_progress import WaitProgress
from journal.features.tasks.tasks_options import TasksOptions


class WaitEstimate:
    """The seconds a wait has left, the longest of what it waits on, unknown when any of them gives no estimate; a wait is short only when it is known and at most the setting's seconds."""

    def __init__(self, remaining: float | None) -> None:
        self.remaining = remaining

    @classmethod
    def create(cls, refs: list[str], progress: Mapping[str, WaitProgress], moment: float) -> "WaitEstimate":
        estimates = [progress[ref].remaining_seconds(moment) if ref in progress else None for ref in refs]
        return cls(None if not estimates or None in estimates else max(estimate for estimate in estimates if estimate is not None))

    def is_short(self, settings: Settings) -> bool:
        return self.remaining is not None and self.remaining <= settings.integer(TasksOptions.SHORT_WAIT_SECONDS)

    def seconds_text(self) -> str:
        return f"about {round(self.remaining)} more seconds" if self.remaining is not None else "for a time the journal cannot estimate yet"
