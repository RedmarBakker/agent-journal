import time
from pathlib import Path

from sync_server.db.store import Store


class ServerBackups:
    """The copies of the team's database written into the backups folder while the server runs, each named for why it was written and when; sync_server restore --from puts one back."""

    def __init__(self, store: Store, folder: Path) -> None:
        self.store, self.folder = store, folder

    def written(self, stem: str) -> Path:
        self.folder.mkdir(parents=True, exist_ok=True)
        target = self.folder / time.strftime(f"{stem}-%Y%m%d-%H%M%S.db")
        self.store.backup(target)
        return target
