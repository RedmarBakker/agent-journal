from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class MessageRead(RowEvent):
    """A message was marked read, with its text when the user wrote it: the agent who read it owes it an answer, once; a comment on a document or report names that writing in words, doc 12, where what it asks is answered."""

    feature_name = "messages"
    user_text: str
    commented_writing: str | None = None
