from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginUpgraded(PluginStanding):
    """A plugin moved to a newer release for the journal's version."""

    previous: str
    tag: str
    version: str
