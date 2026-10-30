from typing import ClassVar

from journal.db.connection import Connection


class Migration:
    """One numbered change to the database after the schema was first created: its statements, run in order, or an up of its own, with a column renamed in place of the empty one the schema already added. has_table is asked of the workers table only for a migration before 50, when workers and verifiers moved to the table of sent agents."""

    number: ClassVar[int]
    statements: ClassVar[tuple[str, ...]] = ()

    def apply(self, connection: Connection) -> None:
        for statement in self.statements:
            connection.execute(statement)

    @staticmethod
    def has_table(connection: Connection, name: str) -> bool:
        return bool(connection.all("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)))

    @staticmethod
    def column_names(connection: Connection, table: str) -> set[str]:
        return {row["name"] for row in connection.all(f"PRAGMA table_info({table})")}

    @staticmethod
    def column_rename(connection: Connection, table: str, old: str, new: str) -> None:
        present = Migration.column_names(connection, table)
        if old not in present:
            return
        if new in present:
            connection.execute(f"ALTER TABLE {table} DROP COLUMN {new}")
        connection.execute(f"ALTER TABLE {table} RENAME COLUMN {old} TO {new}")
