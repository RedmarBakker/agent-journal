from journal.chat.moment_cards import MomentCards
from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.moments.plugin_card_asked import PluginCardAsked
from journal.features.plugins.support.plugin_process_card import PluginProcessCard
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class PluginQuestionCards(Listener[PluginCardAsked]):
    """A card a plugin's answer asks for is a moment card in the chat, or, with a key, a process card that a later card of the key replaces."""

    def __init__(self, cards: MomentCards, processes: ProcessCards, card: PluginProcessCard) -> None:
        self.cards, self.processes, self.card = cards, processes, card

    def handle(self, event: PluginCardAsked) -> None:
        if event.card_key:
            self.processes.show_recent(self.card.card_contents(event))
            return
        self.cards.show_fields(event.environment_id, None, event.label, event.data, Actor.plugin(event.plugin), CardKind.PLUGINS, event.detail)
