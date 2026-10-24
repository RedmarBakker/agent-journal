from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginFailing(PluginStanding):
    """A plugin faulted as many times in a row as marks it failing."""

    fault: str
    failures: int

    def card_parts(self) -> tuple[str, str, str, str]:
        return f"Plugin {self.plugin} is failing: it faulted {self.failures} times in a row, and events go through without it", "bolt", "bad", self.fault
