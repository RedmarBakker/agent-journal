from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

HELPERS_TABLE = "sent_agents"


class HelperRows(Migration):
    """Workers and verifiers are kept in the one table of sent agents, each row's kind saying which: every worker moves over with its number, every verifier takes a number after the last one so none meets a worker's, its links and its card's key following it, and the two old tables go."""

    number: ClassVar[int] = 50

    def apply(self, connection: Connection) -> None:
        if self.has_table(connection, "workers"):
            self.moved(connection, "workers", "worker", "id")
        if self.has_table(connection, "verifiers"):
            self.verifiers_moved(connection)

    def moved(self, connection: Connection, table: str, kind: str, number: str) -> None:
        names = self.shared_columns(connection, table)
        connection.execute(f"INSERT INTO {HELPERS_TABLE} (id, {', '.join(names)}, kind) SELECT {number}, {', '.join(names)}, '{kind}' FROM {table}")
        connection.execute(f"DROP TABLE {table}")

    def verifiers_moved(self, connection: Connection) -> None:
        offset = connection.one(f"SELECT COALESCE(MAX(id), 0) AS value FROM {HELPERS_TABLE}")["value"]
        connection.execute("UPDATE links SET source = 'verifiers:' || (CAST(substr(source, 11) AS INTEGER) + ?) WHERE source LIKE 'verifiers:%'", (offset,))
        connection.execute("UPDATE messages SET data = json_set(data, '$.key', 'verifier:' || (CAST(substr(json_extract(data, '$.key'), 10) AS INTEGER) + ?)) WHERE json_extract(data, '$.key') LIKE 'verifier:%'", (offset,))
        self.moved(connection, "verifiers", "verifier", f"id + {offset}")

    @staticmethod
    def shared_columns(connection: Connection, table: str) -> list[str]:
        present = {row["name"] for row in connection.all(f"PRAGMA table_info({HELPERS_TABLE})")}
        return [row["name"] for row in connection.all(f"PRAGMA table_info({table})") if row["name"] in present and row["name"] not in ("id", "kind")]
