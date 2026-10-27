from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.card_type import CardType


class ReceiptProcessCard(ProcessCard):
    """The process card naming every row linked to one of the user's messages, shown whether or not a reply names it; it changes as rows are linked to the message, and opens the first of them."""

    name = "receipt"

    def __init__(self, messages: Messages, links: Links) -> None:
        self.messages, self.links = messages, links

    def card_contents(self, message: Message) -> ProcessCardContents | None:
        if message.author != Author.USER:
            return None
        receipt_refs = self.links.targets(message, Messages.SUBJECT_LINK)
        key = f"filed:{message.id}"
        if not receipt_refs:
            for card in self.messages.keyed(key, Actor.system()):
                self.messages.delete(card, Actor.system())
            return None
        text = f"Linked {self.labels(receipt_refs)} from your message"
        return ProcessCardContents(self.name, message.environment_id, key, text, {"kind": "card", "row": f"{receipt_refs[0].type}:{receipt_refs[0].id}"}, Actor.system(), CardType.FILED, False)

    @staticmethod
    def labels(refs: list[Ref]) -> str:
        return ", ".join(f"{ref.type.rstrip('s')} {ref.id}" for ref in refs)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
