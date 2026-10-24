import threading
import time

from journal.config import Config

# how long the hook script may keep firing past the last hook the server took before the server counts its hooks as lost
LOST_AFTER_SECONDS = 60


class HookArrivals:
    """The hooks that reach the server beside the ones the hook script fired: the script writes the time of each hook it sends to runtime/hooks/<environment>.fired whether or not the server takes it, and an environment whose script has fired for a minute past the last hook the server took since it started has hooks that no longer reach it."""

    def __init__(self, config: Config) -> None:
        self.folder = config.home / "runtime" / "hooks"
        self.started_at = time.time()
        self.taken: dict[str, float] = {}
        self.lock = threading.Lock()

    def took(self, environment: str) -> None:
        with self.lock:
            self.taken[environment] = time.time()

    def lost(self) -> list[str]:
        return [file.stem for file in sorted(self.folder.glob("*.fired")) if self.fired_at(file.read_text()) - self.last_taken(file.stem) > LOST_AFTER_SECONDS]

    def last_taken(self, environment: str) -> float:
        with self.lock:
            return self.taken.get(environment, self.started_at)

    @staticmethod
    def fired_at(text: str) -> float:
        return float(text.strip()) if text.strip().isdigit() else 0.0
