from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginAnswering(PluginStanding):
    """A plugin that was failing answered again."""
