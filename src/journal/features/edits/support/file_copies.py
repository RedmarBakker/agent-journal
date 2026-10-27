import subprocess
import threading
import time
from pathlib import Path

from journal.config import Config

COPY_COUNT = 200
LARGEST_BYTES = 1_000_000
GIT_SECONDS = 5
STORED_CHARS = 200_000
# a file is read once its size and change time stand still this long, so a rewrite caught between its truncate and its write is never read as emptied
STEADY_SECONDS = 0.05
STEADY_TRIES = 40


class FileCopies:
    """The last version the journal saw of each file the agent changed, so a change a shell command made can be compared line by line, read once the file stands still: against the stored version, or the committed one when there is none."""

    def __init__(self, config: Config) -> None:
        self.root = config.root
        self._copies: dict[str, str] = {}
        self._lock = threading.Lock()

    def last_text(self, path: str) -> str:
        with self._lock:
            if path in self._copies:
                return self._copies[path]
        return self.committed(path)

    def current_text(self, path: str) -> str | None:
        file = self.root / path
        self.steady_wait(file)
        if not file.is_file() or file.stat().st_size > LARGEST_BYTES:
            return None
        return file.read_text(errors="replace")

    @staticmethod
    def steady_wait(file: Path) -> None:
        last = None
        for _ in range(STEADY_TRIES):
            shape = (file.stat().st_size, file.stat().st_mtime_ns) if file.is_file() else None
            if shape == last:
                return
            last = shape
            time.sleep(STEADY_SECONDS)

    def store(self, path: str, text: str) -> None:
        with self._lock:
            self._copies.pop(path, None)
            self._copies[path] = text
            for oldest in list(self._copies)[:-COPY_COUNT]:
                del self._copies[oldest]

    def committed(self, path: str) -> str:
        try:
            shown = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=self.root, capture_output=True, text=True, errors="replace", timeout=GIT_SECONDS)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return shown.stdout if shown.returncode == 0 else ""
