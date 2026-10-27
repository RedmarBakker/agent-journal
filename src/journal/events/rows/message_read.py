from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class MessageRead(RowEvent):
    """A message was marked read: the agent who read it owes it an answer, once."""

    feature_name = "messages"
