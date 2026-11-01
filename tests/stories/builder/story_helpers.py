from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.fixtures.fixture_rows import FixtureRows


class StoryHelpers:
    """The helpers of one role a story names, workers, reviewers or verifiers: the first or the second its fixture made, or any by its number."""

    def __init__(self, role: AgentRole, rows: FixtureRows) -> None:
        self.role, self.rows = role, rows

    def first(self) -> StoryAgent:
        return self.get(self.rows.row("first", 0))

    def second(self) -> StoryAgent:
        return self.get(self.rows.row("second", 0))

    def third(self) -> StoryAgent:
        return self.get(self.rows.row("third", 0))

    def get(self, number: int) -> StoryAgent:
        return StoryAgent(self.role, number)
