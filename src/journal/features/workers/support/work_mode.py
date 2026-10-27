from journal.engine.base_state import BaseState
from journal.engine.support.feature_registry import FeatureRegistry
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows


class WorkMode:
    """The state the work mode the user set puts at the bottom of the stack, asked what that mode does, for code that runs outside the stack: a command, a listener, a measure."""

    def __init__(self, settings: SettingRows, registry: FeatureRegistry) -> None:
        self.settings, self.registry = settings, registry

    def state(self) -> type[BaseState]:
        modes = next(modes for modes in self.registry.modes() if modes.option == WorkersOptions.MODE)
        return modes.states[str(self.settings.option(WorkersOptions.MODE))]

    def delegates_work(self) -> bool:
        return self.state().delegates_work()
