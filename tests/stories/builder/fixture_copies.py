from tests.stories.builder.fixture_copy import FixtureCopy
from tests.stories.fixtures.state_fixture import StateFixture


class FixtureCopies:
    """Each state fixture of a module's journal seeded once per provider and kept as a copy: a story starts from the copy, and a fixture that builds on another is seeded from that one's copy, so a story's setup never grows with its fixture chain."""

    def __init__(self) -> None:
        self.copies: dict[tuple[type, str], FixtureCopy] = {}

    def reached(self, story, fixture: type[StateFixture]) -> StateFixture:
        copy = self.copies.get((fixture, story.provider))
        return copy.put_back(story) if copy is not None else self.seeded(story, fixture)

    def seeded(self, story, fixture: type[StateFixture]) -> StateFixture:
        reached = fixture()
        if fixture.builds_on is not None:
            reached.inherits(self.reached(story, fixture.builds_on))
        reached.steps(story)
        reached.expected(story)
        self.copies[(fixture, story.provider)] = FixtureCopy.taken(story, reached)
        return reached.copied()
