from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.deleted import Deleted
from journal.features.messages.support.receipt_process_card import ReceiptProcessCard
from journal.models.link import Link
from journal.models.message import Message
from journal.repositories.messages import Messages
from journal.support.missing_row import MissingRow


class ReceiptLinkRemoval(Listener[Deleted]):
    """A link from one of the user's messages that is removed, such as the guess a --from replaces, takes its row off the message's receipt card, and the card goes once nothing is linked."""

    def __init__(self, messages: Messages, card: ReceiptProcessCard, cards: ProcessCards) -> None:
        self.messages, self.card, self.cards = messages, card, cards

    def handle(self, event: Deleted) -> None:
        for message in self.subjects(event.model):
            contents = self.card.card_contents(message)
            if contents:
                self.cards.show(contents)

    def subjects(self, row) -> list[Message]:
        if not (isinstance(row, Link) and row.link_type == Messages.SUBJECT_LINK and row.source.type == Message.table()):
            return []
        try:
            return [self.messages.find(row.source.id)]
        except MissingRow:
            return []
