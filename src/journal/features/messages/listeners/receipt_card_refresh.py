from typing import TypeVar

from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.model_event import ModelEvent
from journal.features.messages.support.receipt_process_card import ReceiptProcessCard
from journal.models.message import Message
from journal.models.model import Model
from journal.repositories.messages import Messages
from journal.support.missing_row import MissingRow

E = TypeVar("E", bound=ModelEvent)


class ReceiptCardRefresh(Listener[E]):
    """The parent of the listeners that show again the receipt card of each of the user's messages a written or removed row touches, for every message that still has rows to name."""

    def __init__(self, messages: Messages, card: ReceiptProcessCard, cards: ProcessCards) -> None:
        self.messages, self.card, self.cards = messages, card, cards

    def handle(self, event: E) -> None:
        for message in self.subjects(event.model):
            contents = self.card.card_contents(message)
            if contents:
                self.cards.show(contents)

    def subjects(self, row: Model) -> list[Message]:
        return []

    def present_message(self, number: int) -> list[Message]:
        try:
            return [self.messages.find(number)]
        except MissingRow:
            return []
