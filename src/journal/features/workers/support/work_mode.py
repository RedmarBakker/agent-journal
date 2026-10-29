from journal.engine.base_state import BaseState
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.settings import Settings
from journal.repositories.setting_rows import SettingRows


class WorkMode:
    """The state the settings put at the bottom of the stack, asked what that mode does, for code that runs outside the stack: a command, a listener, a measure."""

    def __init__(self, settings: SettingRows, catalogue: StatesCatalogue) -> None:
        self.settings, self.catalogue = settings, catalogue

    def state(self) -> type[BaseState]:
        return self.catalogue.mode_state(Settings.applied(self.settings, self.catalogue.mode_options()))

    def delegates_work(self) -> bool:
        return self.state().delegates_work()
