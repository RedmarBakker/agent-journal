from datetime import datetime
from pathlib import Path

from journal.config import Config
from journal.engine.job import Job
from journal.features.health.health_options import HealthOptions
from journal.repositories.journal_backup import JournalBackup
from journal.repositories.setting_rows import SettingRows


class DatabaseBackup(Job):
    """Once the minutes the setting names have passed since the newest copy, an online copy of the journal's database is written to .journal/backups-watch, as many of the newest left as the setting keeps, so a damaged file loses those minutes at most."""

    interval_seconds = 60.0

    def __init__(self, config: Config, backup: JournalBackup, settings: SettingRows) -> None:
        self.config, self.backup, self.settings = config, backup, settings

    def tick(self, time: float) -> None:
        minutes = self.settings.integer(HealthOptions.BACKUP_MINUTES)
        copies = self.copies()
        if not minutes or (copies and time - copies[0].stat().st_mtime < 60 * minutes):
            return
        self.folder().mkdir(parents=True, exist_ok=True)
        self.backup.write(self.folder() / f"journal-{datetime.fromtimestamp(time).strftime('%Y%m%d-%H%M%S')}.db")
        for extra_copy in self.copies()[self.settings.integer(HealthOptions.BACKUP_COUNT):]:
            extra_copy.unlink()

    def folder(self) -> Path:
        return self.config.home / "backups-watch"

    def copies(self) -> list[Path]:
        return sorted(self.folder().glob("journal-*.db"), reverse=True)
