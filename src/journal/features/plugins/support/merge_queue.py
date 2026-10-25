from collections.abc import Iterator
from contextlib import contextmanager
from threading import Condition

from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows


class MergeQueue:
    """The worker merges that plugins are asked about at once; a merge past the setting waits here for a place within the seconds it is given, and one that finds none goes on without asking."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings, self.asked, self.condition = settings, 0, Condition()

    def has_place(self) -> bool:
        limit = self.settings.integer(WorkersOptions.MERGE_LIMIT)
        return limit == 0 or self.asked < limit

    @contextmanager
    def place(self, seconds: float) -> Iterator[bool]:
        with self.condition:
            placed = self.condition.wait_for(self.has_place, seconds)
            if placed:
                self.asked += 1
        try:
            yield placed
        finally:
            if placed:
                with self.condition:
                    self.asked -= 1
                    self.condition.notify_all()
