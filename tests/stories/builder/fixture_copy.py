from dataclasses import dataclass

from tests.shared_journal import SharedJournal
from tests.stories.fixtures.state_fixture import StateFixture


@dataclass(frozen=True)
class FixtureCopy:
    """A state fixture as its seeder left the journal: the journal's rows, files and services, the fixture with the rows it named, and the lines its seeding made the journal say, put back for every later story that starts from it."""

    journal: SharedJournal
    fixture: StateFixture
    line_keys: frozenset[str]
    main_session_id: str
    session_environments: tuple[tuple[str, str], ...]

    @staticmethod
    def journal_copy(story, fixture: StateFixture) -> "FixtureCopy":
        return FixtureCopy(SharedJournal(story.app), fixture, frozenset(story.line_keys), story.main_session_id,
                           tuple(story.session_environments.items()))

    def restore(self, story) -> StateFixture:
        self.journal.put_back()
        story.team_servers_restarted()
        story.line_keys |= self.line_keys
        environments = dict(self.session_environments)
        story.replace_main_session(self.main_session_id, story.provider,
                                   environments.get(self.main_session_id, "main"))
        story.session_environments = environments
        return self.fixture.copied()
