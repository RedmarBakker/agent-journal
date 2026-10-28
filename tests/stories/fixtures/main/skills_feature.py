from journal.features.skills.feature import Skills
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class SkillsFeature(StateFixture):
    """The agent at work, with the skills feature switched on by the user, so the skills a moment names are owed."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.user_switches_on(Skills)

    def expected(self, story) -> None:
        story.expect_stack(Ready)
