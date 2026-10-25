import time

from journal.config import Config
from journal.events.announcer import Announcer
from journal.events.moments.boot_failed import BootFailed
from journal.version import VERSION

BOOT_NOTICE = "boot_failures.txt"
BOOT_SECONDS = "boot_seconds"


class BootNotices:
    """What went wrong at boot, told once the journal answers: the faults of its own seeds, and the lines the supervisor left in a notice file when it started a boot again or took it back to the last version that booted."""

    def __init__(self, config: Config, announcer: Announcer) -> None:
        self.config, self.announcer = config, announcer
        self._faults: list[str] = []

    def add(self, text: str) -> None:
        self._faults.append(text)

    def announce(self) -> None:
        notice = self.config.home / "runtime" / BOOT_NOTICE
        lines = notice.read_text().replace("{version}", VERSION).splitlines() if notice.is_file() else []
        notice.unlink(missing_ok=True)
        faults, self._faults = [*lines, *self._faults], []
        for text in faults:
            self.announcer.announce(BootFailed(text=text, time=time.time()))

    def write_boot_seconds(self, seconds: float) -> None:
        path = self.config.home / "runtime" / BOOT_SECONDS
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(seconds))
