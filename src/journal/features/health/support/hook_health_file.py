from journal.config import Config
from journal.features.health.health_options import HealthOptions
from journal.repositories.setting_rows import SettingRows

FILE_NAME = "hook-health-seconds"


class HookHealthFile:
    """The runtime file the hook and shell scripts read the seconds they wait for the journal's health answer from, written from its setting, since the scripts start no Python."""

    def __init__(self, config: Config, settings: SettingRows) -> None:
        self.config, self.settings = config, settings

    def write(self) -> None:
        path = self.config.home / "runtime" / FILE_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{self.settings.integer(HealthOptions.HOOK_HEALTH_SECONDS)}\n")
