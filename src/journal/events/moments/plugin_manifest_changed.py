from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginManifestChanged(PluginStanding):
    """A linked plugin's manifest changed in its folder and waits for the user to apply it."""

    changes: str

    def card_parts(self) -> tuple[str, str, str, str]:
        return f"Plugin {self.plugin}'s manifest changed in its folder; it runs as installed until you apply it with journal plugin upgrade {self.plugin} --yes", "plug", "warn", self.changes
