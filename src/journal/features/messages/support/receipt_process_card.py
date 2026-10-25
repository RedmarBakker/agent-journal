from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.features.messages.support.hub_mentions import HubMentions
from journal.models.author import Author
from journal.models.message import Message
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class ReceiptProcessCard(ProcessCard):
    """The process card naming every row filed from one of the user's messages that no reply of the agent's to it names; it changes as rows are filed and replies name them, and goes once they all are."""

    name = "receipt"

    def __init__(self, messages: Messages, links: Links, mentions: HubMentions) -> None:
        self.messages, self.links, self.mentions = messages, links, mentions

    def card_contents(self, message: Message) -> ProcessCardContents | None:
        if message.author != Author.USER:
            return None
        reply_refs = {ref for reply in self.messages.replies(message) for ref in self.mentions.found(reply.text)}
        receipt_refs = self.links.targets_except(message, Messages.SUBJECT_LINK, reply_refs)
        key = f"filed:{message.id}"
        if not receipt_refs:
            for card in self.messages.keyed(key, Actor.system()):
                self.messages.delete(card, Actor.system())
            return None
        receipt_text = ", ".join(f"{ref.type.rstrip('s')} {ref.id}" for ref in receipt_refs)
        return ProcessCardContents(self.name, message.environment_id, key, f"Filed {receipt_text} from your message", {"kind": "card", "row": f"messages:{message.id}"}, Actor.system(), CardKind.FILED, False)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
