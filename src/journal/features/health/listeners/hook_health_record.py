from journal.events.listener import Listener
from journal.events.rows.setting_changed import SettingChanged
from journal.features.health.health_options import HealthOptions
from journal.features.health.support.hook_health_file import HookHealthFile


class HookHealthRecord(Listener[SettingChanged]):
    """A change of the hook scripts' health wait is written to the file they read."""

    def __init__(self, file: HookHealthFile) -> None:
        self.file = file

    def handle(self, event: SettingChanged) -> None:
        if event.setting == HealthOptions.HOOK_HEALTH_SECONDS.key:
            self.file.write()
