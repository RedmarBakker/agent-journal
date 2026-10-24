from journal.console.support.chained_line import ChainedLine
from journal.repositories.setting_rows import SettingRows
from journal.features.briefing.briefing_options import BriefingOptions


class OverviewCommands:
    """The command lines the overview after a compaction or a takeover hands the console to run, in the order the setting names them."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def lines(self) -> list[ChainedLine]:
        return [ChainedLine(command) for command in self.settings.texts(BriefingOptions.OVERVIEW_COMMANDS)]
