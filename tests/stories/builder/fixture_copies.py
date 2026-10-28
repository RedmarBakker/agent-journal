from tests.stories.builder.fixture_copy import FixtureCopy
from tests.stories.fixtures.state_fixture import StateFixture


class FixtureCopies:
    """Each state fixture of a module's journal seeded once per provider and kept as a copy: a story starts from the copy, and a fixture that builds on another is seeded from that one's copy, so a story's setup never grows with its fixture chain; the steps each seeding played are kept, for the run to lay the fixtures over each other as it does the stories, and the settings a fixture set that its seeding never read, for each story from it to read."""

    def __init__(self) -> None:
        self.copies: dict[tuple[type, str], FixtureCopy] = {}
        self.seedings: dict[tuple[type, str], list[str]] = {}
        self.settings_left: dict[tuple[type, str], tuple[str, ...]] = {}

    def reached(self, story, fixture: type[StateFixture]) -> StateFixture:
        copy = self.copies.get((fixture, story.provider))
        return copy.restore(story) if copy is not None else self.seeded(story, fixture)

    def seeded(self, story, fixture: type[StateFixture]) -> StateFixture:
        reached = fixture()
        if fixture.parent is not None:
            reached.inherits(self.reached(story, fixture.parent))
        mark = len(story.path)
        for option, value in fixture.settings:
            story.user_sets(option, value)
        reached.steps(story)
        reached.expected(story)
        self.settings_left[(fixture, story.provider)] = tuple(story.unread_settings())
        self.seedings[(fixture, story.provider)] = [f"starts from {fixture.parent.__name__ if fixture.parent else 'nothing'}", *story.path[mark:]]
        self.copies[(fixture, story.provider)] = FixtureCopy.journal_copy(story, reached)
        return reached.copied()
