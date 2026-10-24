from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginFailing(PluginStanding):
    """A plugin faulted as many times in a row as marks it failing."""

    fault: str
