from journal.events.models.deleted import Deleted
from journal.features.messages.listeners.receipt_card_refresh import ReceiptCardRefresh
from journal.models.link import Link
from journal.models.message import Message
from journal.models.model import Model
from journal.repositories.messages import Messages


class ReceiptLinkRemoval(ReceiptCardRefresh[Deleted]):
    """A link from one of the user's messages that is removed, such as the guess a --from replaces, takes its row off the message's receipt card, and the card goes once nothing is linked."""

    def subjects(self, row: Model) -> list[Message]:
        if not (isinstance(row, Link) and row.link_type == Messages.SUBJECT_LINK and row.source.type == Message.table()):
            return []
        return self.present_message(row.source.id)
