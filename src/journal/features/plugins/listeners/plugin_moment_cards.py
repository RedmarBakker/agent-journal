from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.plugin_standing import PluginStanding
from journal.support.card_kind import CardKind


class PluginMomentCards(Listener[PluginStanding]):
    """Each moment of a plugin that is not its own card is one mark in the chat of the environment it happened in: failing, answering again, switched off, a manifest waiting, upgraded, not upgraded."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: PluginStanding) -> None:
        label, icon, tone, detail = event.card_parts()
        self.cards.show(event.environment_id, "", label, icon, tone=tone, detail=detail, shows=CardKind.PLUGINS)
