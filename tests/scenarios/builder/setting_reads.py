from journal.engine.support.settings import Settings
from journal.repositories.setting_rows import SettingRows


class SettingReads:
    """Every setting the journal reads while a story plays, in order, by its key, caught where every read passes, the states' Settings and the rows' option, so a story can ask whether a setting it set was ever read after it set it."""

    def __init__(self) -> None:
        self.keys: list[str] = []

    def watch(self, monkeypatch) -> None:
        state_value, row_option = Settings.value, SettingRows.option

        def state_read(settings, option):
            self.keys.append(option.key)
            return state_value(settings, option)

        def row_read(rows, option):
            self.keys.append(option.key)
            return row_option(rows, option)

        monkeypatch.setattr(Settings, "value", state_read)
        monkeypatch.setattr(SettingRows, "option", row_read)

    def position(self) -> int:
        return len(self.keys)

    def is_read_since(self, key: str, position: int) -> bool:
        return key in self.keys[position:]
