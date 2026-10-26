from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows


class OrchestratorMode:
    """Whether the user set the orchestrator work mode."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def is_set(self) -> bool:
        return self.settings.option(WorkersOptions.MODE) == "orchestrator"
