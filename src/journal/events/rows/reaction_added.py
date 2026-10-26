from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ReactionAdded(RowEvent):
    """An emoji was put on a message, by the user or by the agent."""

    feature_name = "messages"

    emoji: str
    message_id: int
    user_origin: bool
