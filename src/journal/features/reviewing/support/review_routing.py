from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.workers.support.work_mode import WorkMode
from journal.repositories.setting_rows import SettingRows

class ReviewRouting:
    """Whether a worker's clock-out goes to the journal's reviewer rather than to the agent that sent it: in orchestrator mode with the reviewer on."""

    def __init__(self, settings: SettingRows, work_mode: WorkMode) -> None:
        self.settings, self.work_mode = settings, work_mode

    def is_enabled(self) -> bool:
        return self.work_mode.delegates_work() and bool(self.settings.option(ReviewingOptions.REVIEWER))
