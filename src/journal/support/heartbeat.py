import os
from pathlib import Path

HEARTBEAT_FILE = "heartbeat"
HEARTBEAT_INTERVAL_SECONDS = 10.0
LIMIT_SECONDS = 30.0


class Heartbeat:
    """The time a running chain's watcher writes into its output folder every ten seconds while its shell lives, so a command that computes for an hour without printing still reads as alive, and one whose process is gone reads so thirty seconds after its last beat, or after it began when it never beat."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def write(self, seconds: float) -> None:
        part_path = self.folder / f"{HEARTBEAT_FILE}.part"
        part_path.write_text(str(seconds))
        os.replace(part_path, self.folder / HEARTBEAT_FILE)

    def last_seconds(self) -> float:
        path = self.folder / HEARTBEAT_FILE
        text = path.read_text().strip() if path.is_file() else ""
        return float(text) if text else 0.0

    def is_running(self, seconds: float, began_seconds: float) -> bool:
        return seconds - (self.last_seconds() or began_seconds) < LIMIT_SECONDS
