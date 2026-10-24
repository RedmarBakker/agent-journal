from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginUpgraded(PluginStanding):
    """A plugin moved to a newer release for the journal's version."""

    previous: str
    tag: str
    version: str

    def card_parts(self) -> tuple[str, str, str, str]:
        return f"Plugin {self.plugin} upgraded from {self.previous} to {self.tag} for journal {self.version}", "plug", "", ""
