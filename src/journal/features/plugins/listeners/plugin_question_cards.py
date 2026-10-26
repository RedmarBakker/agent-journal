from journal.chat.moment_cards import MomentCards
from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.moments.plugin_card_requested import PluginCardRequested
from journal.features.plugins.support.plugin_process_card import PluginProcessCard
from journal.support.actor import Actor
from journal.support.card_type import CardType


class PluginQuestionCards(Listener[PluginCardRequested]):
    """A card a plugin's answer asks for is a moment card in the chat, or, with a key, a process card that a later card of the key replaces, unless it says the same, which leaves the card where it is."""

    def __init__(self, cards: MomentCards, processes: ProcessCards, card: PluginProcessCard) -> None:
        self.cards, self.processes, self.card = cards, processes, card

    def handle(self, event: PluginCardRequested) -> None:
        if event.card_key:
            contents = self.card.card_contents(event)
            if not self.processes.is_unchanged(contents):
                self.processes.show_recent(contents)
            return
        self.cards.show_fields(event.environment_id, None, event.label, event.data, Actor.plugin(event.plugin), CardType.PLUGINS, event.detail)
