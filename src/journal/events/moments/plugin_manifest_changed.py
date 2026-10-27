from journal.support.card_outcome import CardOutcome
from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginManifestChanged(PluginStanding):
    """A linked plugin's manifest changed in its folder and waits for the user to apply it."""

    changes: str

    def card_parts(self) -> tuple[str, CardOutcome, str]:
        return f"Plugin {self.plugin} has a newer version waiting to be applied", CardOutcome.WARNED, self.changes
