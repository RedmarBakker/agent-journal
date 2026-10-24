from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginNotUpgraded(PluginStanding):
    """A plugin could not be moved to a newer release for the journal's version."""

    version: str
    reason: str
