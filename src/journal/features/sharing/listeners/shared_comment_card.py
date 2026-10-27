from journal.events.listener import Listener
from journal.events.moments.shared_comment_posted import SharedCommentPosted
from journal.models.author import Author
from journal.models.link import Link
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor

VISITOR = "visitor"


class SharedCommentCard(Listener[SharedCommentPosted]):
    """A visitor's comment is a card of the journal's in the chat, linked to the row as its comment, and never the user's own words."""

    def __init__(self, messages: Messages, links: Links) -> None:
        self.messages, self.links = messages, links

    def handle(self, event: SharedCommentPosted) -> Message:
        message = self.messages.save(Message(author=Author.SYSTEM, text=f"{event.name} commented on {event.row} through a shared link",
                                             data={"kind": "card", "detail": event.text, "row": str(event.row), VISITOR: event.name, "share": event.share}), Actor.system())
        self.links.save(Link(source=Ref.build(message), target=event.row, link_type=Messages.COMMENT_LINK), Actor.system())
        return message
