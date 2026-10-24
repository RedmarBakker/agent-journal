from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginSwitchedOff(PluginStanding):
    """A plugin was switched off because files it runs changed since it was installed or switched on."""

    changed: str
