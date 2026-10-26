from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class MessageThreadColumn(Migration):
    """A message's chat is its thread column, where it was the agent_role column, so the agents' roles name agents only and the people's side thread is a thread like the agents' chats."""

    number: ClassVar[int] = 65

    def apply(self, connection: Connection) -> None:
        self.column_rename(connection, "messages", "agent_role", "thread")
