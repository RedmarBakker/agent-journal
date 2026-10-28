from collections.abc import Callable

from journal.support.option import Option
from tests.full_project import MAIN
from tests.in_process import got


class StorySugar:
    """Short ways to say what a story does many times: a step repeated, as many tool uses as a setting allows, each one let through, and a setting read back through the viewer's route as the journal holds it."""

    def repeat(self, times: int, step: Callable[[], None]) -> None:
        for _ in range(times):
            step()

    def agent_consumes(self, option: Option) -> None:
        for _ in range(int(self.setting(option))):
            self.agent_reads()
            self.expect_allowed()

    def expect_setting(self, option: Option, value: object) -> None:
        held = self.setting(option)
        assert held == value, f"{option.key} is held as {held!r}, not {value!r}"

    def setting(self, option: Option) -> object:
        tree = got(self.app, "/journal/settings", MAIN)[1]
        for part in option.key.split("."):
            tree = tree.get(part, {}) if isinstance(tree, dict) else {}
        return option.default if tree == {} else tree
