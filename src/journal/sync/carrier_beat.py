import json
import os
import time

from journal.config import Config

BEAT_FILE = "sync-status.json"
# how long the carrier's last beat may be old before it counts as gone
STALE_SECONDS = 10


class CarrierBeat:
    """runtime/sync-status.json, which the sync carrier in a process of its own writes every second, its pid, the time and the fault it meets, and the server reads for the status line: a beat gone stale says the sync process is not running; no file, a carrier in the server's own threads."""

    def __init__(self, config: Config) -> None:
        self.path = config.home / "runtime" / BEAT_FILE

    def beat(self, fault: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        draft = self.path.with_suffix(".draft")
        draft.write_text(json.dumps({"pid": os.getpid(), "beat_at": time.time(), "fault": fault}))
        draft.replace(self.path)

    def fault(self) -> str:
        if not self.path.is_file():
            return ""
        beat = json.loads(self.path.read_text())
        if time.time() - beat["beat_at"] > STALE_SECONDS:
            return "the sync process is not running"
        return beat["fault"]

    def forget(self) -> None:
        self.path.unlink(missing_ok=True)
