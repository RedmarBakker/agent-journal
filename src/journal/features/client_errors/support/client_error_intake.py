from journal.engine.support.nudge_log import NudgeLog
from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.client_errors_options import ClientErrorsOptions
from journal.repositories.setting_rows import SettingRows
from journal.features.client_errors.support.client_error_store import ClientErrorStore


class ClientErrorIntake:
    """Keeps an error the viewer posted, and tells the agent at once when it is one the store did not hold and the setting asks for it."""

    def __init__(self, store: ClientErrorStore, nudges: NudgeLog, settings: SettingRows) -> None:
        self.store, self.nudges, self.settings = store, nudges, settings

    def record(self, message: str, stack: str) -> None:
        if self.store.add(message, stack) and self.settings.option(ClientErrorsOptions.REPORT):
            self.nudges.type(ClientErrorsNudges.LOGGED.create(errors=ClientErrorsNudges.errors(self.store.count())))
