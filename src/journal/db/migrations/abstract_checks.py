from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.models.support.abstract_text import ABSTRACT_LENGTH_CHARACTERS, AbstractText

ABSTRACT_TABLES = ("reports", "docs")
# the abstract column as a table with the database's check on it declares it
CHECKED_ABSTRACT = f"abstract TEXT NOT NULL CHECK (length(abstract) BETWEEN 1 AND {ABSTRACT_LENGTH_CHARACTERS})"


class AbstractChecks(Migration):
    """Every report and document has an abstract the database checks: one missing or too long is written as its body's first sentence cut to the limit, then each table is made again with its abstract column NOT NULL and its length checked, its rows and indexes carried over."""

    number: ClassVar[int] = 66

    def apply(self, connection: Connection) -> None:
        for table in [table for table in ABSTRACT_TABLES if self.has_table(connection, table)]:
            self.filled(connection, table)
            self.rebuilt(connection, table)

    @staticmethod
    def filled(connection: Connection, table: str) -> None:
        rows = connection.all(f"SELECT id, COALESCE(title, '') AS title, COALESCE(body, '') AS body, COALESCE(abstract, '') AS abstract FROM {table}")
        for row in [row for row in rows if AbstractText.refusal(row["abstract"])]:
            connection.execute(f"UPDATE {table} SET abstract = ? WHERE id = ?", (AbstractText.body_abstract(row["body"], row["title"]), row["id"]))

    @staticmethod
    def rebuilt(connection: Connection, table: str) -> None:
        made = connection.result("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (table,))["sql"]
        if "CHECK (length(abstract)" in made:
            return
        indexes = [row["sql"] for row in connection.all("SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = ? AND sql IS NOT NULL", (table,))]
        connection.execute(f"ALTER TABLE {table} RENAME TO {table}_unchecked")
        connection.execute(made.replace("abstract TEXT", CHECKED_ABSTRACT, 1))
        connection.execute(f"INSERT INTO {table} SELECT * FROM {table}_unchecked")
        connection.execute(f"DROP TABLE {table}_unchecked")
        for index in indexes:
            connection.execute(index)
