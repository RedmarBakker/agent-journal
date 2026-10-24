from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginDisabled(PluginStanding):
    """A plugin was switched off because files it runs changed since it was installed or switched on."""

    changed: str

    def card_parts(self) -> tuple[str, str, str, str]:
        return f"Plugin {self.plugin} is off: {self.changed} changed since you installed it or switched it on. Read the change, then switch it on with journal plugin enable {self.plugin}", "bolt", "bad", ""
