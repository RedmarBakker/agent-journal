from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.plugin_answering import PluginAnswering
from journal.events.moments.plugin_failing import PluginFailing
from journal.events.moments.plugin_manifest_changed import PluginManifestChanged
from journal.events.moments.plugin_not_upgraded import PluginNotUpgraded
from journal.events.moments.plugin_standing import PluginStanding
from journal.events.moments.plugin_switched_off import PluginSwitchedOff
from journal.events.moments.plugin_upgraded import PluginUpgraded
from journal.features.plugins.support.plugin_faults import FAILURE_COUNT
from journal.support.card_kind import CardKind


class PluginMomentCards(Listener[PluginStanding]):
    """Each moment of a plugin that is not its own card is one mark in the chat of the environment it happened in: failing, answering again, switched off, a manifest waiting, upgraded, not upgraded."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: PluginStanding) -> None:
        label, icon, tone, detail = self.words(event)
        self.cards.show(event.environment_id, "", label, icon, tone=tone, detail=detail, shows=CardKind.PLUGINS)

    @staticmethod
    def words(event: PluginStanding) -> tuple[str, str, str, str]:
        name = event.plugin
        if isinstance(event, PluginFailing):
            return f"Plugin {name} is failing: it faulted {FAILURE_COUNT} times in a row, and events go through without it", "bolt", "bad", event.fault
        if isinstance(event, PluginAnswering):
            return f"Plugin {name} answers again", "check", "good", ""
        if isinstance(event, PluginSwitchedOff):
            return f"Plugin {name} is off: {event.changed} changed since you installed it or switched it on. Read the change, then switch it on with journal plugin enable {name}", "bolt", "bad", ""
        if isinstance(event, PluginManifestChanged):
            return f"Plugin {name}'s manifest changed in its folder; it runs as installed until you apply it with journal plugin upgrade {name} --yes", "plug", "warn", event.changes
        if isinstance(event, PluginUpgraded):
            return f"Plugin {name} upgraded from {event.previous} to {event.tag} for journal {event.version}", "plug", "good", ""
        if isinstance(event, PluginNotUpgraded):
            return f"Plugin {name} was not upgraded for journal {event.version}: {event.reason}", "plug", "bad", ""
        raise TypeError(f"no mark is written for {type(event).__name__}")
