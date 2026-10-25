from collections.abc import Iterator
from contextlib import contextmanager
from threading import Condition

from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows


class MergeQueue:
    """The worker merges that plugins are asked about at once; a merge past the setting waits here for a place, and its wait is not counted against its window."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings, self.asked, self.condition = settings, 0, Condition()

    def has_place(self) -> bool:
        limit = self.settings.integer(WorkersOptions.MERGE_LIMIT)
        return limit == 0 or self.asked < limit

    @contextmanager
    def place(self) -> Iterator[None]:
        with self.condition:
            self.condition.wait_for(self.has_place)
            self.asked += 1
        try:
            yield
        finally:
            with self.condition:
                self.asked -= 1
                self.condition.notify_all()
