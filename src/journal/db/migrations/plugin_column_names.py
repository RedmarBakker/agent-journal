from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

# the plugins table's columns renamed for the plain-name rules, old name to new
PLUGIN_COLUMNS = {"off_on_purpose": "is_user_disabled", "waits_for": "wait_target"}


class PluginColumnNames(Migration):
    """The plugins table's columns renamed for the plain-name rules take their new names, so a plugin keeps whether the user switched it off and the journal version it waits for."""

    number: ClassVar[int] = 46

    def apply(self, connection: Connection) -> None:
        for old, new in PLUGIN_COLUMNS.items():
            self.column_rename(connection, "plugins", old, new)
