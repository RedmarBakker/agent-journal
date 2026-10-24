from datetime import datetime

from journal.models.check import Check
from journal.repositories.repository import Repository
from journal.support.actor import Actor


class Checks(Repository[Check]):
    model = Check

    def all(self) -> list[Check]:
        return self.newest(self.query().filter(wait_target=False, is_retired=False))

    def due(self, time: datetime) -> list[Check]:
        return [check for check in self.rows() if check.needs_run(time)]

    def plugin_rows(self, plugin: str) -> list[Check]:
        return self.all_matching(creator=Actor.plugin(plugin).stamp, is_retired=False)

    def broken_waits(self) -> list[Check]:
        return [check for check in self.all_matching(wait_target=True) if check.cannot_run() and not check.is_resolved()]
