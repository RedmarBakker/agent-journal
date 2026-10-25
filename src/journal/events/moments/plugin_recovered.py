from journal.support.card_outcome import CardOutcome
from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginRecovered(PluginStanding):
    """A plugin that was failing answered again."""

    def card_parts(self) -> tuple[str, CardOutcome, str]:
        return f"Plugin {self.plugin} answers again", CardOutcome.PASSED, ""
