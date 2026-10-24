from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginUpgradeFailed(PluginStanding):
    """A plugin could not be moved to a newer release for the journal's version."""

    version: str
    reason: str

    def card_parts(self) -> tuple[str, str, str, str]:
        return f"Plugin {self.plugin} was not upgraded for journal {self.version}: {self.reason}", "plug", "bad", ""
