from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginManifestChanged(PluginStanding):
    """A linked plugin's manifest changed in its folder and waits for the user to apply it."""

    changes: str
