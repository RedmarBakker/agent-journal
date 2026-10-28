from dataclasses import dataclass

from tests.shared_journal import SharedJournal
from tests.stories.fixtures.state_fixture import StateFixture


@dataclass(frozen=True)
class FixtureCopy:
    """A state fixture as its seeder left the journal: the journal's rows, files and services, the fixture with the rows it named, and the lines its seeding made the journal say, put back for every later story that starts from it."""

    journal: SharedJournal
    fixture: StateFixture
    said_keys: frozenset[str]

    @staticmethod
    def taken(story, fixture: StateFixture) -> "FixtureCopy":
        return FixtureCopy(SharedJournal(story.app), fixture, frozenset(story.said_keys))

    def put_back(self, story) -> StateFixture:
        self.journal.put_back()
        story.said_keys |= self.said_keys
        return self.fixture.copied()
