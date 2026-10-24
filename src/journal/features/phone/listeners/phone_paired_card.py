from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.models.phone import Phone
from journal.support.card_kind import CardKind


class PhonePairedCard(Listener[Created]):
    """A phone that pairs is one mark in the chat of the environment it was paired for."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: Created) -> None:
        if isinstance(event.model, Phone):
            self.cards.show(event.model.environment_id, "", f"A phone paired: {event.model.name}", "phone", shows=CardKind.PHONES)
