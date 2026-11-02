import threading
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

from journal.config import Config


class RigFolders:
    """The published rig folders, replaced under the same per-rig guard their readers use."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._guard = threading.Lock()
        self._locks: dict[str, AbstractContextManager] = {}

    def path(self, rig: str) -> Path:
        return self.config.home / "runtime" / "rigs" / rig

    def locked(self, rig: str) -> AbstractContextManager:
        with self._guard:
            return self._locks.setdefault(rig, threading.RLock())

    @contextmanager
    def replacing(self, rig: str) -> Iterator[Path]:
        folder = self.path(rig)
        folder.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=f".{rig}-", dir=folder.parent) as temporary:
            staged, previous = Path(temporary) / "next", Path(temporary) / "previous"
            staged.mkdir()
            yield staged
            with self.locked(rig):
                if folder.exists():
                    folder.rename(previous)
                try:
                    staged.rename(folder)
                except OSError:
                    if previous.exists():
                        previous.rename(folder)
                    raise
