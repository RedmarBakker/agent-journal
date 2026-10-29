from pathlib import Path

from journal.config import Config
from journal.features.workers.organization_options import OrganizationOptions
from journal.repositories.setting_rows import SettingRows


class ContractFolder:
    """The folder the setting names as the agentic organization, the only class that reads that setting; a relative path is read from the project root."""

    def __init__(self, settings: SettingRows, config: Config) -> None:
        self.settings, self.config = settings, config

    def path(self) -> Path | None:
        named = str(self.settings.option(OrganizationOptions.FOLDER)).strip()
        return self.config.root / named if named else None
