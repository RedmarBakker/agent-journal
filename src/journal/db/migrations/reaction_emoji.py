from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class ReactionEmoji(Migration):
    """A reaction's emoji column takes the plain name emoji, so every reaction keeps its value."""

    number: ClassVar[int] = 41

    def apply(self, connection: Connection) -> None:
        self.column_rename(connection, "reactions", "face", "emoji")
