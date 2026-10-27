import shutil
import time
from pathlib import Path

from sync_server.db.store import Store


class ServerBackups:
    """The copies of the team's database written into the backups folder while the server runs, each named for why it was written and when, with the library's item files copied beside it in a folder of the same name ending .items; sync_server restore --from puts both back."""

    def __init__(self, store: Store, folder: Path, items: Path) -> None:
        self.store, self.folder, self.items = store, folder, items

    def written(self, stem: str) -> Path:
        self.folder.mkdir(parents=True, exist_ok=True)
        return self.copied(self.folder / time.strftime(f"{stem}-%Y%m%d-%H%M%S.db"))

    def copied(self, target: Path) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        self.store.backup(target)
        if self.items.is_dir():
            shutil.copytree(self.items, self.items_copy(target), dirs_exist_ok=True)
        return target

    def restored(self, source: Path) -> None:
        self.store.restore(source)
        if self.items_copy(source).is_dir():
            shutil.rmtree(self.items, ignore_errors=True)
            shutil.copytree(self.items_copy(source), self.items)

    @staticmethod
    def items_copy(database: Path) -> Path:
        return database.with_suffix(".items")
