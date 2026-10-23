from dataclasses import dataclass

from journal.models.message import Message


@dataclass(frozen=True)
class ChatRow:
    """One message a hydration writes into the chat, with the time its transcript gives it."""

    message: Message
    time: float
