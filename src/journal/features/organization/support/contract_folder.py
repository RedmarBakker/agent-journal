from pathlib import Path

from journal.config import Config
from journal.features.organization.support.contract_revision import ContractRevision
from journal.features.workers.organization_options import OrganizationOptions
from journal.repositories.setting_rows import SettingRows


class ContractFolder:
    """The folder the setting names as the agentic organization, the only class that reads that setting and the version beside it; a relative path is read from the project root, and with a version set the files are those of that git version, extracted, not the checked-out ones."""

    def __init__(self, settings: SettingRows, config: Config, revision: ContractRevision) -> None:
        self.settings, self.config, self.revision = settings, config, revision

    def named(self) -> Path | None:
        named = str(self.settings.option(OrganizationOptions.FOLDER)).strip()
        return self.config.root / named if named else None

    def version(self) -> str:
        return str(self.settings.option(OrganizationOptions.VERSION)).strip()

    def path(self) -> Path | None:
        folder = self.named()
        return self.revision.extracted(folder, self.version()) if folder and folder.is_dir() and self.version() else folder
