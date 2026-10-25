from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.trigger_fired import TriggerFired
from journal.support.card_kind import CardKind


class TriggerCard(Listener[TriggerFired]):
    """A trigger that matched is one mark in the chat with the phrases that matched it."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: TriggerFired) -> None:
        self.cards.show(event.environment_id, event.session, f"Trigger {event.text}", ", ".join(event.phrases), event.ref, shows=CardKind.TRIGGERS)
