from journal.support.card_outcome import CardOutcome
from dataclasses import dataclass

from journal.events.moments.plugin_standing import PluginStanding


@dataclass(frozen=True, kw_only=True)
class PluginFailing(PluginStanding):
    """A plugin faulted as many times in a row as marks it failing."""

    fault: str
    failures: int

    def card_parts(self) -> tuple[str, CardOutcome, str]:
        return f"Plugin {self.plugin} is failing: it faulted {self.failures} times in a row, and events go through without it", CardOutcome.FAILED, self.fault
