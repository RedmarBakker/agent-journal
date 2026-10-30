import shutil
import time
from pathlib import Path

OLD_TABLES = ("messages", "dumps")


class OldRowFiles:
    """The files the row sync attached to messages and dumps, which nothing on the server points at any more: moved whole out of the files folder into the backups folder, where a backup holds them, the first time a server starts without the sync."""

    def __init__(self, files: Path, backups: Path) -> None:
        self.files, self.backups = files, backups

    def moved(self) -> list[Path]:
        folders = [self.files / table for table in OLD_TABLES if (self.files / table).is_dir()]
        if not folders:
            return []
        target = self.backups / time.strftime("row-files-%Y%m%d-%H%M%S")
        target.mkdir(parents=True, exist_ok=True)
        return [Path(shutil.move(str(folder), str(target / folder.name))) for folder in folders]
