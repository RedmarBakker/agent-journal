from journal.db.connection import Connection
from journal.db.index import Index

STATISTICS = "PRAGMA optimize=0x10002"


class Indexes:
    """Every index the journal's reads rely on, made at each boot on a new database and an upgraded one alike: one missing is made, and one whose definition changed is made again; then the table statistics the query planner chooses an index by are brought up to date."""

    def __init__(self, connection: Connection, declared: tuple[Index, ...]) -> None:
        self.connection, self.declared = connection, declared

    def refresh(self) -> None:
        present = {row["name"]: row["sql"] for row in self.connection.all("SELECT name, sql FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL")}
        with self.connection.transaction() as db:
            for index in self.declared:
                if present.get(index.name) == index.sql():
                    continue
                db.execute(f"DROP INDEX IF EXISTS {index.name}")
                db.execute(index.sql())
        self.connection.execute(STATISTICS)
