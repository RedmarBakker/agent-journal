import threading

from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.support.option import Option
from journal.support.wrong_setting_type import WrongSettingType
from journal.models.setting import Setting
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.time_source import TimeSource



class SettingRows(ScopedRepository[Setting]):
    """Reads a key with the project's value over the environment's; writes to the scope requested, and writes nothing for a value it already holds. Each scope's values are cached until a setting is written, not cached when a write cleared them while they were being read, and kept apart on the thread whose write has not committed yet, until its next write, so it reads what it wrote while other threads read what is committed."""

    model = Setting

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource) -> None:
        super().__init__(connection, bus, scope, time_source)
        self._kept: dict[int, list[Setting]] = {}
        self._values: dict[int, dict[str, object]] = {}
        self._clear_count = 0
        self._writing = threading.local()

    def get(self, key: str, default: object = None) -> object:
        return self.merged().get(key, default)

    def project(self, key: str, default: object = None) -> object:
        return self.project_values().get(key, default)

    def option(self, option: Option) -> object:
        if option.behind is not None and not self.option(option.behind):
            return False
        return self.project(option.key, option.default)

    def mapping(self, key: str) -> dict:
        value = self.project(key, {})
        if not isinstance(value, dict):
            raise WrongSettingType(key, value)
        return value

    def texts(self, option: Option) -> tuple[str, ...]:
        return option.texts(self.option(option))

    def integer(self, option: Option) -> int:
        return option.integer(self.option(option))

    def decimal(self, option: Option) -> float:
        return option.decimal(self.option(option))

    def set(self, key: str, value: object, actor) -> Setting:
        rows = [s for s in self.project_rows() if s.key == key]
        if rows and rows[0].value == value:
            return rows[0]
        return self.save((rows[0] if rows else Setting(environment_id=PROJECT, key=key)).with_value(value, self._time().timestamp()), actor)

    def with_line(self, option: Option, line: str, actor) -> Setting:
        return self.set(option.key, [*self.lines_without(option, line), line], actor)

    def without_line(self, option: Option, line: str, actor) -> Setting:
        return self.set(option.key, self.lines_without(option, line), actor)

    def lines_without(self, option: Option, line: str) -> list[str]:
        return [text for text in self.texts(option) if text != line]

    def unset(self, key: str, actor) -> None:
        for row in [s for s in self.project_rows() if s.key == key]:
            self.delete(row, actor)

    def tree(self) -> dict:
        return self.nested(self.merged())

    def project_tree(self) -> dict:
        return self.nested(self.project_values())

    @staticmethod
    def nested(values: dict) -> dict:
        tree: dict = {}
        for key, value in values.items():
            top, name = key.split(".", 1) if "." in key else (key, "")
            tree.setdefault(top, {})[name] = value
        return tree

    def merged(self) -> dict:
        return self.values(self.scope.id)

    def project_values(self) -> dict:
        return self.values(PROJECT)

    def values(self, environment_id: int) -> dict:
        if self.is_writing():
            return self.thread_values(self._writing.values, environment_id, self.read_values)
        if environment_id in self._values:
            return self._values[environment_id]
        clear_count = self._clear_count
        merged = self.read_values(environment_id)
        if clear_count == self._clear_count:
            self._values[environment_id] = merged
        return merged

    def read_values(self, environment_id: int) -> dict:
        environment_values = {setting.key: setting.value for setting in self.environment_rows(environment_id)}
        return environment_values if environment_id == PROJECT else environment_values | self.project_values()

    def project_rows(self) -> list[Setting]:
        return self.environment_rows(PROJECT)

    def environment_rows(self, environment_id: int) -> list[Setting]:
        if self.is_writing():
            return self.thread_values(self._writing.rows, environment_id, lambda scope_id: self.global_matching(environment_id=scope_id))
        if environment_id in self._kept:
            return self._kept[environment_id]
        clear_count = self._clear_count
        rows = self.global_matching(environment_id=environment_id)
        if clear_count == self._clear_count:
            self._kept[environment_id] = rows
        return rows

    def is_writing(self) -> bool:
        return getattr(self._writing, "is_open", False)

    @staticmethod
    def thread_values(scope_values: dict, environment_id: int, read) -> object:
        if environment_id not in scope_values:
            scope_values[environment_id] = read(environment_id)
        return scope_values[environment_id]

    def stored(self) -> None:
        super().stored()
        self._writing.is_open, self._writing.values, self._writing.rows = True, {}, {}
        self.clear_cache()
        self.connection.commit_callback(self.committed)

    def committed(self) -> None:
        self._writing.is_open = False
        self.clear_cache()

    def clear_cache(self) -> None:
        self._clear_count += 1
        self._kept.clear()
        self._values.clear()

    def _placed(self, row: Setting) -> Setting:
        return row
