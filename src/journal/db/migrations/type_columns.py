import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.models.edit import Edit
from journal.models.entry import Entry
from journal.models.environment import Environment
from journal.models.helper import Helper
from journal.models.link import Link
from journal.models.report import Report
from journal.models.secret import Secret

RENAMED = (Entry, Link, Helper, Secret, Edit, Environment, Report)
FORMER_KEY = "kind"
# the key a sequence's triggers and an edit's rows hold their type under now, by table and column
RECORD_KEYS = {("sequences", "triggers"): "trigger_type", ("edits", "rows"): "line_type"}


class TypeColumns(Migration):
    """The columns named kind take their model's type name, entry_type or link_type, so a row keeps its value, every index on the empty column the schema already added dropped first so that column can go, to be made again at boot; and a sequence's triggers and an edit's rows hold theirs as trigger_type and line_type."""

    number: ClassVar[int] = 75

    def apply(self, connection: Connection) -> None:
        for model in RENAMED:
            for old, new in model.column_renames.items():
                self.index_drop(connection, model.storage(), new)
                self.column_rename(connection, model.storage(), old, new)
        for (table, column), key in RECORD_KEYS.items():
            self.record_rename(connection, table, column, key)

    @staticmethod
    def record_rename(connection: Connection, table: str, column: str, key: str) -> None:
        for row in connection.all(f"SELECT id, {column} FROM {table} WHERE {column} LIKE ?", (f'%"{FORMER_KEY}"%',)):
            records = [{(key if name == FORMER_KEY else name): value for name, value in record.items()} for record in json.loads(row[column])]
            connection.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (json.dumps(records), row["id"]))

    @staticmethod
    def index_drop(connection: Connection, table: str, column: str) -> None:
        for index in connection.all("SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = ? AND sql LIKE ?", (table, f"%{column}%")):
            connection.execute(f"DROP INDEX IF EXISTS {index['name']}")
