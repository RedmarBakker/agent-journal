from journal.events.models.created import Created
from journal.features.messages.listeners.receipt_card_refresh import ReceiptCardRefresh
from journal.models.link import Link
from journal.models.message import Message
from journal.models.model import Model
from journal.repositories.messages import Messages


class DumpItemCard(ReceiptCardRefresh[Created]):
    """A row filed from one of the user's messages is a process card in the chat, ReceiptProcessCard, one per message, naming every row filed from it that no reply of the agent's to the message names; once the replies name them all, the mark goes."""

    def subjects(self, row: Model) -> list[Message]:
        if isinstance(row, Link) and row.link_type in (Messages.SUBJECT_LINK, Messages.EDIT_LINK) and row.source.type == Message.table():
            return [self.messages.find(row.source.id)]
        if isinstance(row, Message) and row.is_agent_message() and row.reply_target:
            return self.present_message(row.reply_target)
        return []
