from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

DROPPED_COLUMNS = {
    "environments": ("kind", "environment_type", "team_key", "team_name", "worktree_host"),
    "docs": ("edit_mode", "owner", "is_copy"),
    "doc_revisions": ("is_copy",),
}
TEAM_LINKS = ("bound_to", "drive_ended", "requested_of", "requested_of_team", "issue", "owner", "copied_from", "attached_to")


class TeamColumnsDrop(Migration):
    """The hub and the sharing between people are gone: a hub's and a session's environment rows are deleted, the columns that named an environment's team, kind and worktree machine and a document's place on the hub are dropped, a colleague's comment becomes the user's message, and the links that bound, requested, owned, copied or attached rows across the team are deleted."""

    number: ClassVar[int] = 79

    def apply(self, connection: Connection) -> None:
        environment_columns = self.column_names(connection, "environments")
        for column in ("kind", "environment_type"):
            if column in environment_columns:
                connection.execute(f"DELETE FROM environments WHERE {column} IN ('hub', 'session')")
        for table, columns in DROPPED_COLUMNS.items():
            present = self.column_names(connection, table)
            for column in (column for column in columns if column in present):
                connection.execute(f"ALTER TABLE {table} DROP COLUMN {column}")
        connection.execute("UPDATE messages SET author = 'user' WHERE author = 'colleague'")
        connection.execute(f"DELETE FROM links WHERE link_type IN ({', '.join('?' for _ in TEAM_LINKS)})", TEAM_LINKS)
