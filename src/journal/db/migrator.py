import time
from datetime import datetime, timezone

from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.db.migration_failure import MigrationFailure
from journal.db.migration_failures import MigrationFailures
from journal.db.schema import Schema


class Migrator:
    """Runs the migrations not recorded yet, each in a transaction of its own: one that raises is rolled back, reported in the failures and left unrecorded so the next start runs it again, and the ones after it still run."""

    def __init__(self, connection: Connection, schema: Schema, migrations: tuple[Migration, ...] = (), failures: MigrationFailures | None = None) -> None:
        self.connection, self.schema, self.migrations = connection, schema, migrations
        self.failures = failures if failures is not None else MigrationFailures()

    def pending(self) -> list[Migration]:
        recorded = {row["number"] for row in self.connection.all("SELECT number FROM migrations")}
        return sorted((m for m in self.migrations if m.number not in recorded), key=lambda m: m.number)

    def record_all(self) -> None:
        with self.connection.transaction() as db:
            for migration in self.migrations:
                db.execute("INSERT OR IGNORE INTO migrations (number, ran_at) VALUES (?, ?)", (migration.number, datetime.now(timezone.utc).isoformat()))

    def run(self) -> list[Migration]:
        completed = []
        for migration in self.pending():
            try:
                with self.connection.transaction() as db:
                    migration.apply(db)
                    db.execute("INSERT INTO migrations (number, ran_at) VALUES (?, ?)", (migration.number, datetime.now(timezone.utc).isoformat()))
            except Exception as fault:
                self.failures.add(MigrationFailure(migration.number, f"{type(fault).__name__}: {fault}", time.time()))
                continue
            completed.append(migration)
        if completed:
            self.connection.cache.cleared()
        return completed
