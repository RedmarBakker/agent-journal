from dataclasses import dataclass

from tests.shared_journal import SharedJournal
from tests.stories.fixtures.state_fixture import StateFixture


@dataclass(frozen=True)
class FixtureCopy:
    """A state fixture as its seeder left the journal: the journal's rows, files and services, the fixture with the rows it named, and the lines its seeding made the journal say, put back for every later story that starts from it."""

    journal: SharedJournal
    fixture: StateFixture
    line_keys: frozenset[str]

    @staticmethod
    def journal_copy(story, fixture: StateFixture) -> "FixtureCopy":
        return FixtureCopy(SharedJournal(story.app), fixture, frozenset(story.line_keys))

    def restore(self, story) -> StateFixture:
        self.journal.put_back()
        story.line_keys |= self.line_keys
        return self.fixture.copied()
