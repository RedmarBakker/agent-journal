from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

HELPERS_TABLE = "sent_agents"
# the sent agents' type column, named kind before migration 75 and helper_type after, as a table the schema makes today has it
TYPE_COLUMNS = ("kind", "helper_type")


class HelperRows(Migration):
    """Workers and verifiers are kept in the one table of sent agents, each row's type saying which, in the type column the table of sent agents has: every worker moves over with its number, every verifier takes a number after the last one so none meets a worker's, its links and its card's key following it, and the two old tables go."""

    number: ClassVar[int] = 50

    def apply(self, connection: Connection) -> None:
        if self.has_table(connection, "workers"):
            self.moved(connection, "workers", "worker", "id")
        if self.has_table(connection, "verifiers"):
            self.verifiers_moved(connection)

    def moved(self, connection: Connection, table: str, type_name: str, number: str) -> None:
        names = self.shared_columns(connection, table)
        connection.execute(f"INSERT INTO {HELPERS_TABLE} (id, {', '.join(names)}, {self.type_column(connection)}) SELECT {number}, {', '.join(names)}, '{type_name}' FROM {table}")
        connection.execute(f"DROP TABLE {table}")

    def verifiers_moved(self, connection: Connection) -> None:
        offset = connection.one(f"SELECT COALESCE(MAX(id), 0) AS value FROM {HELPERS_TABLE}")["value"]
        connection.execute("UPDATE links SET source = 'verifiers:' || (CAST(substr(source, 11) AS INTEGER) + ?) WHERE source LIKE 'verifiers:%'", (offset,))
        connection.execute("UPDATE messages SET data = json_set(data, '$.key', 'verifier:' || (CAST(substr(json_extract(data, '$.key'), 10) AS INTEGER) + ?)) WHERE json_extract(data, '$.key') LIKE 'verifier:%'", (offset,))
        self.moved(connection, "verifiers", "verifier", f"id + {offset}")

    @staticmethod
    def shared_columns(connection: Connection, table: str) -> list[str]:
        present = HelperRows.helper_columns(connection)
        return [row["name"] for row in connection.all(f"PRAGMA table_info({table})") if row["name"] in present and row["name"] not in ("id", *TYPE_COLUMNS)]

    @staticmethod
    def type_column(connection: Connection) -> str:
        return next(column for column in TYPE_COLUMNS if column in HelperRows.helper_columns(connection))

    @staticmethod
    def helper_columns(connection: Connection) -> set[str]:
        return {row["name"] for row in connection.all(f"PRAGMA table_info({HELPERS_TABLE})")}
