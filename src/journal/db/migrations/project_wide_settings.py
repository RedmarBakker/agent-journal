from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

SETTINGS = "settings"
PROJECT = 0


class ProjectWideSettings(Migration):
    """Settings are the project's alone: a key stored only for an environment moves to the project, its newest row kept, and every other row an environment held is removed, a key the project already holds keeping the project's value it was read as."""

    number: ClassVar[int] = 74

    def apply(self, connection: Connection) -> None:
        if not self.has_table(connection, SETTINGS):
            return
        project_keys = {row["key"] for row in connection.all("SELECT key FROM settings WHERE environment_id = ?", (PROJECT,))}
        newest: dict[str, int] = {}
        for row in connection.all("SELECT id, key FROM settings WHERE environment_id != ? ORDER BY id", (PROJECT,)):
            if row["key"] not in project_keys:
                newest[row["key"]] = row["id"]
        for row_id in newest.values():
            connection.execute("UPDATE settings SET environment_id = ? WHERE id = ?", (PROJECT, row_id))
        connection.execute("DELETE FROM settings WHERE environment_id != ?", (PROJECT,))
