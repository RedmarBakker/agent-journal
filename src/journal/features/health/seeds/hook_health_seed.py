from journal.features.health.support.hook_health_file import HookHealthFile
from journal.features.seed import Seed


class HookHealthSeed(Seed):
    """At boot, the hook scripts' health wait is written from its setting."""

    def __init__(self, file: HookHealthFile) -> None:
        self.file = file

    def run(self) -> None:
        self.file.write()
