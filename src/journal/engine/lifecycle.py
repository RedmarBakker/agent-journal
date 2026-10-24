import os
import threading
import time

from journal.config import Config
from journal.engine.lifecycle_phase import LifecyclePhase

BOOTING_FILE = "journal.booting"
RESTART = "restart"


class Lifecycle:
    """The server's phase, owned by the engine: the runtime's start puts it in booting, and while it boots nothing runs and every request waits; once booted the waits are let through, as they are for a server started with nothing to boot. A file in the runtime folder says it boots, holding the booting server's process id, so the hook script and the command shim wait for it, and stop waiting once that process is gone; a restart writes the old server's id after the word restart, so once the old server is gone they wait across the gap for the next one too, a short while at most."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.phase = LifecyclePhase.BOOTED
        self._booted = threading.Event()
        self._booted.set()

    def marker(self):
        return self.config.home / "runtime" / BOOTING_FILE

    def booting(self) -> None:
        self.phase = LifecyclePhase.BOOTING
        self._booted.clear()
        self.write_marker(str(os.getpid()))

    def restarting(self) -> None:
        self.write_marker(f"{RESTART} {os.getpid()}")

    def write_marker(self, process: str) -> None:
        self.marker().parent.mkdir(parents=True, exist_ok=True)
        self.marker().write_text(process)

    def booted(self) -> None:
        self.phase = LifecyclePhase.BOOTED
        self._booted.set()
        self.marker().unlink(missing_ok=True)

    def is_booted(self) -> bool:
        return self._booted.is_set()

    def boot_wait_seconds(self) -> float:
        began = time.monotonic()
        self._booted.wait()
        return time.monotonic() - began
