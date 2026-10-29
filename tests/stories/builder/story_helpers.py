from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent


class StoryHelpers:
    """The helpers of one role a story names, workers, reviewers or verifiers: the first its fixture made, or any by its number."""

    def __init__(self, role: AgentRole, first_number: int) -> None:
        self.role, self.first_number = role, first_number

    def first(self) -> StoryAgent:
        return self.get(self.first_number)

    def get(self, number: int) -> StoryAgent:
        return StoryAgent(self.role, number)
