from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReplyPosted(RowEvent):
    """The agent's reply to a message is in the chat, by the message it answers."""

    feature_name = "messages"

    reply_target: int
