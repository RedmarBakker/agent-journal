from journal.features.workers.workers_options import WorkersOptions
from journal.models.support.report_use import ReportUse
from journal.repositories.setting_rows import SettingRows


class ReportUseMeasuring:
    """How often its workers interrupted an agent, measured from the reports on its row with the user's numbers: the window, what counts as plenty open, the rates at full and at no score, and a drop's recovery minutes."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def measured(self, use: ReportUse, time: float) -> ReportUse:
        rates = (self.settings.decimal(WorkersOptions.INTERRUPTIONS_FULL), self.settings.decimal(WorkersOptions.INTERRUPTIONS_ZERO))
        return use.measured(time, self.settings.decimal(WorkersOptions.INTERRUPTION_WINDOW), self.settings.integer(WorkersOptions.PLENTY_OPEN), rates, self.settings.decimal(WorkersOptions.DROP_RECOVERY_MINUTES))
