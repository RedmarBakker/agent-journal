from dataclasses import dataclass
from typing import Callable

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.features.workers.support.workers_data import WorkersData
from journal.support.option import Option


@dataclass(frozen=True)
class Alignment:
    """One rule of a work mode's alignment, configured in Python: the mode it speaks in, the count it reads from what the journal keeps, the option that sets its limit, and the line said once the count reaches it, which repeats only after its nudge's repeat span; it never holds anything."""

    mode: str
    count: Callable[[WorkersData], int]
    limit: Option
    nudge: Nudge

    def line(self, mode: str, workers: WorkersData, settings: Settings) -> Nudge | None:
        if mode != self.mode:
            return None
        limit = settings.integer(self.limit)
        if limit <= 0 or self.count(workers) < limit:
            return None
        return self.nudge.create(count=self.count(workers), limit=limit)
