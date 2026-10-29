from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding
from journal.support.card_outcome import CardOutcome


@dataclass(frozen=True, kw_only=True)
class PluginUpdateAvailable(PluginStanding):
    """A newer release of a plugin runs on the journal's version, offered for the user to review and install."""

    previous: str
    tag: str

    def card_parts(self) -> tuple[str, CardOutcome, str]:
        return f"Plugin {self.plugin} has update {self.tag} available", CardOutcome.NONE, f"Installed: {self.previous}. Review the update on the Plugins page; it installs only when you press Install."
