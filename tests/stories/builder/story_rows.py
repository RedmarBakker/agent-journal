from tests.stories.fixtures.fixture_rows import FixtureRows
from tests.stories.fixtures.state_fixture import StateFixture


class StoryRows:
    """The rows a story's fixture made, read by their kind and name: story.tasks.started, story.plans.first, story.messages.second; the helpers it made are read from story.agents."""

    fixture: StateFixture

    @property
    def tasks(self) -> FixtureRows:
        return self.fixture.tasks

    @property
    def plans(self) -> FixtureRows:
        return self.fixture.plans

    @property
    def messages(self) -> FixtureRows:
        return self.fixture.messages

    @property
    def sequences(self) -> FixtureRows:
        return self.fixture.sequences

    @property
    def plugins(self) -> FixtureRows:
        return self.fixture.plugins

    @property
    def aliases(self) -> FixtureRows:
        return self.fixture.aliases

    @property
    def documents(self) -> FixtureRows:
        return self.fixture.documents

    @property
    def readers(self) -> FixtureRows:
        return self.fixture.readers

    @property
    def outputs(self) -> FixtureRows:
        return self.fixture.outputs

    @property
    def memories(self) -> FixtureRows:
        return self.fixture.memories
