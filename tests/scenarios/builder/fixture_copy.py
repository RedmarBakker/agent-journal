from dataclasses import dataclass

from tests.shared_journal import SharedJournal


@dataclass(frozen=True)
class FixtureCopy:
    """A state fixture as its seeder left the journal: the journal's rows, files and services, the rows the fixture named and the lines its seeding made the journal say, put back for every later story that starts from it."""

    journal: SharedJournal
    rows: dict[str, int]
    row_makers: dict[str, type]
    said_keys: frozenset[str]

    @staticmethod
    def taken(scenario) -> "FixtureCopy":
        return FixtureCopy(SharedJournal(scenario.app), dict(scenario.rows), dict(scenario.row_makers), frozenset(scenario.said_keys))

    def put_back(self, scenario) -> None:
        self.journal.put_back()
        scenario.rows.update(self.rows)
        scenario.row_makers.update(self.row_makers)
        scenario.said_keys |= self.said_keys
