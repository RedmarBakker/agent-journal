from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.messages.support.receipt_process_card import ReceiptProcessCard
from journal.models.author import Author
from journal.models.link import Link
from journal.models.message import Message
from journal.repositories.messages import Messages
from journal.support.missing_row import MissingRow


class DumpItemCard(Listener[Created]):
    """A row filed from one of the user's messages is a process card in the chat, ReceiptProcessCard, one per message, naming every row filed from it that no reply of the agent's to the message names; once the replies name them all, the mark goes."""

    def __init__(self, messages: Messages, card: ReceiptProcessCard, cards: ProcessCards) -> None:
        self.messages, self.card, self.cards = messages, card, cards

    def handle(self, event: Created) -> None:
        for message in self.subjects(event.model):
            contents = self.card.card_contents(message)
            if contents:
                self.cards.show(contents)

    def subjects(self, row) -> list[Message]:
        if isinstance(row, Link) and row.kind == Messages.SUBJECT_LINK and row.source.type == Message.table():
            return [self.messages.find(row.source.id)]
        if isinstance(row, Message) and row.author == Author.AGENT and row.reply_target:
            return self.requested(row.reply_target)
        return []

    def requested(self, n: int) -> list[Message]:
        try:
            return [self.messages.find(n)]
        except MissingRow:
            return []
