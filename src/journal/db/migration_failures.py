from journal.db.migration_failure import MigrationFailure


class MigrationFailures:
    """The migrations that failed at this boot, in the order they ran, for the log and the viewer to report."""

    def __init__(self) -> None:
        self.rows: list[MigrationFailure] = []

    def add(self, failure: MigrationFailure) -> None:
        self.rows.append(failure)

    def lines(self) -> list[str]:
        return [f"migration {row.number} failed at {row.at:.0f} and will be tried again at the next start: {row.error}" for row in self.rows]
