from dataclasses import dataclass

from journal.events.rows.reaction_added import ReactionAdded
from journal.support.message_thread import MessageThread
from journal.models.author import Author
from journal.models.message import Message
from journal.models.scoped import Scoped


@dataclass(frozen=True)
class Reaction(Scoped):
    """One emoji by one side on one message; the message it sits on is a link of kind reacts."""

    emoji: str = ""
    author: Author = Author.USER

    def reacted_message(self, message: Message) -> "Reaction":
        if message.thread != MessageThread.MAIN:
            return self
        return self.with_event(ReactionAdded(environment_id=self.environment_id, emoji=self.emoji, message_id=message.row_id, user_origin=self.author == Author.USER))
