from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.repositories.setting_rows import SettingRows

class ReviewRouting:
    """Whether a worker's clock-out goes to the journal's reviewer rather than to the agent that sent it."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def is_enabled(self) -> bool:
        return bool(self.settings.option(ReviewingOptions.REVIEWER))
