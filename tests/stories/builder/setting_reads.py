from threading import local

from journal.engine.support.settings import Settings
from journal.repositories.setting_rows import SettingRows


class SettingReads:
    """Every setting the journal's code asks for while a story plays, in order, by its key: what a state asks of its Settings and what other code asks of the rows, never the copy of every option the engine takes for each event, so a setting stored and never asked for shows as unread."""

    def __init__(self) -> None:
        self.keys: list[str] = []
        self.copying = local()

    def watch(self, monkeypatch) -> None:
        state_value, row_option, copied = Settings.value, SettingRows.option, Settings.applied.__func__

        def state_read(settings, option):
            self.keys.append(option.key)
            return state_value(settings, option)

        def row_read(rows, option):
            if not getattr(self.copying, "active", False):
                self.keys.append(option.key)
            return row_option(rows, option)

        def copy(cls, rows, options):
            was_copying = getattr(self.copying, "active", False)
            self.copying.active = True
            try:
                return copied(cls, rows, options)
            finally:
                self.copying.active = was_copying

        monkeypatch.setattr(Settings, "value", state_read)
        monkeypatch.setattr(SettingRows, "option", row_read)
        monkeypatch.setattr(Settings, "applied", classmethod(copy))

    def position(self) -> int:
        return len(self.keys)

    def is_read(self, key: str, position: int) -> bool:
        return key in self.keys[position:]
