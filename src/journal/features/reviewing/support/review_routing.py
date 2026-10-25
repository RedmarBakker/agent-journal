from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows

ORCHESTRATOR = "orchestrator"


class ReviewRouting:
    """Whether a worker's clock-out goes to the journal's reviewer rather than to the agent that sent it: in orchestrator mode with the reviewer on."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def is_enabled(self) -> bool:
        return self.settings.option(WorkersOptions.MODE) == ORCHESTRATOR and bool(self.settings.option(ReviewingOptions.REVIEWER))
